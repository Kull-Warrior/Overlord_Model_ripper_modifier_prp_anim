import bpy
import math
import struct
from mathutils import Matrix, Vector, Quaternion

from myFunction import GAME_TO_BLENDER, GAME_TO_BLENDER_INV, game_quaternion
from skeletonLib import bone_rest_data

# blender frame of game frame 0
FRAME_OFFSET = 1

ROT_TYPE_QUAT_XYZ = 22
SCALE_TYPE = 30

class ActionBone:
	def	__init__(self):
		self.name = None
		self.position_keys = []      # (time_us, (x, y, z)), game space
		self.rotation_keys = []      # Quaternion per frame, game space
		self.raw_rotation = []
		self.raw_signs = b''

	def decode_rotation(self, records, signs):
		# int16 x,y,z * 32767, sign of w in the bit array
		self.raw_rotation = list(records)
		self.raw_signs = bytes(signs)
		self.rotation_keys = []
		previous = None
		for i, raw in enumerate(records):
			x, y, z = [v / 32767.0 for v in struct.unpack('<3h', raw)]
			w = math.sqrt(max(0.0, 1.0 - (x * x + y * y + z * z)))
			if i >> 3 < len(signs) and (signs[i >> 3] >> (i & 7)) & 1:
				w = -w
			q = game_quaternion(x, y, z, w)
			q.normalize()
			if previous is not None and previous.dot(q) < 0.0:
				q.negate()
			self.rotation_keys.append(q)
			previous = q

	def position_at(self, time_us):
		keys = self.position_keys
		if not keys:
			return None
		if len(keys) == 1 or time_us <= keys[0][0]:
			return Vector(keys[0][1])
		for i in range(len(keys) - 1):
			t0, p0 = keys[i]
			t1, p1 = keys[i + 1]
			if t0 <= time_us <= t1:
				f = float(time_us - t0) / float(t1 - t0) if t1 > t0 else 0.0
				return Vector(p0).lerp(Vector(p1), f)
		return Vector(keys[-1][1])

class Action:
	def __init__(self):
		self.name = 'action'
		self.fps = 15.0
		self.duration_us = 0
		self.bone_list = []
		self.blender_action = None

	def frame_count(self):
		n = int(round(self.duration_us * self.fps / 1000000.0)) + 1
		for bone in self.bone_list:
			n = max(n, len(bone.rotation_keys))
		return max(n, 1)

	def bone_names(self):
		return set(bone.name for bone in self.bone_list)

	def matches(self, bone_names):
		if not self.bone_list:
			return 0.0
		common = len(self.bone_names() & set(bone_names))
		return float(common) / float(len(self.bone_list))

	def draw(self, armature_object, action_name=None, set_active=True):
		# keys are absolute local transforms: basis = K^-1 * rest^-1 * anim * K
		scene = bpy.context.scene
		scene_fps = float(scene.render.fps) / float(scene.render.fps_base)
		frame_scale = scene_fps / self.fps if self.fps > 0 else 1.0

		action = bpy.data.actions.new(action_name if action_name else self.name)
		action.use_fake_user = True
		self.blender_action = action
		new_fcurve, slot = _fcurve_factory(action, armature_object)

		pose_bones = armature_object.pose.bones
		animated = set()
		end_frame = FRAME_OFFSET

		# some files contain a second degenerate track for a bone, keep the bigger one
		tracks = {}
		for action_bone in self.bone_list:
			other = tracks.get(action_bone.name)
			if other is None or len(action_bone.rotation_keys) + len(action_bone.position_keys) > len(other.rotation_keys) + len(other.position_keys):
				tracks[action_bone.name] = action_bone

		for action_bone in tracks.values():
			pose_bone = pose_bones.get(action_bone.name)
			if pose_bone is None:
				continue
			rest_local, orient = bone_rest_data(armature_object, action_bone.name)
			if rest_local is None:
				continue
			animated.add(action_bone.name)
			pose_bone.rotation_mode = 'QUATERNION'

			rest_rotation_inv = rest_local.to_3x3()
			rest_rotation_inv.normalize()
			rest_rotation_inv.invert()
			rest_translation = rest_local.to_translation()
			orient3 = orient.to_3x3()
			orient3_inv = orient3.inverted()
			C3 = GAME_TO_BLENDER.to_3x3()

			quats = []
			previous = None
			for i, q in enumerate(action_bone.rotation_keys):
				anim_rotation = C3 @ q.to_matrix() @ C3.transposed()
				basis = orient3_inv @ rest_rotation_inv @ anim_rotation @ orient3
				bq = basis.to_quaternion()
				if previous is not None and previous.dot(bq) < 0.0:
					bq.negate()
				quats.append(bq)
				previous = bq
			if not quats:
				quats = [Quaternion((1.0, 0.0, 0.0, 0.0))]
			frames = [FRAME_OFFSET + i * frame_scale for i in range(len(quats))]
			end_frame = max(end_frame, frames[-1])
			group = action_bone.name
			for component in range(4):
				fc = new_fcurve('pose.bones["%s"].rotation_quaternion' % pose_bone.name, component, group)
				_fill_fcurve(fc, frames, [q[component] for q in quats])

			locations = []
			if action_bone.position_keys:
				for time_us, position in action_bone.position_keys:
					anim_translation = C3 @ Vector(position)
					basis_translation = orient3_inv @ (rest_rotation_inv @ (anim_translation - rest_translation))
					frame = FRAME_OFFSET + (time_us * self.fps / 1000000.0) * frame_scale
					locations.append((frame, basis_translation))
				if len(action_bone.position_keys) == 1:
					locations = [(FRAME_OFFSET, locations[0][1])]
			else:
				locations = [(FRAME_OFFSET, Vector((0.0, 0.0, 0.0)))]
			frames = [_snap_frame(f) for f, _ in locations]
			end_frame = max(end_frame, frames[-1])
			for component in range(3):
				fc = new_fcurve('pose.bones["%s"].location' % pose_bone.name, component, group)
				_fill_fcurve(fc, frames, [v[component] for _, v in locations])

		# bones without a track stay in the rest pose
		for pose_bone in pose_bones:
			if pose_bone.name in animated:
				continue
			pose_bone.rotation_mode = 'QUATERNION'
			for component, value in enumerate((1.0, 0.0, 0.0, 0.0)):
				fc = new_fcurve('pose.bones["%s"].rotation_quaternion' % pose_bone.name, component, pose_bone.name)
				_fill_fcurve(fc, [FRAME_OFFSET], [value])
			for component in range(3):
				fc = new_fcurve('pose.bones["%s"].location' % pose_bone.name, component, pose_bone.name)
				_fill_fcurve(fc, [FRAME_OFFSET], [0.0])

		last_frame = FRAME_OFFSET + (self.frame_count() - 1) * frame_scale
		last_frame = max(last_frame, end_frame)
		try:
			action.use_frame_range = True
			action.frame_start = FRAME_OFFSET
			action.frame_end = last_frame
		except Exception:
			pass

		if set_active:
			assign_action(armature_object, action, slot)
			scene.frame_start = FRAME_OFFSET
			scene.frame_end = int(math.ceil(last_frame))
			scene.frame_current = FRAME_OFFSET
		return action

def assign_action(armature_object, action, slot=None):
	if armature_object.animation_data is None:
		armature_object.animation_data_create()
	armature_object.animation_data.action = action
	if hasattr(action, 'slots'):
		try:
			if slot is None and len(action.slots) > 0:
				slot = action.slots[0]
			if slot is not None:
				armature_object.animation_data.action_slot = slot
		except Exception as e:
			print('	Warning: could not assign action slot:', e)

def _snap_frame(frame, tolerance=1e-3):
	r = round(frame)
	return float(r) if abs(frame - r) < tolerance else frame

def _fill_fcurve(fcurve, frames, values):
	points = fcurve.keyframe_points
	points.add(len(frames))
	co = [0.0] * (2 * len(frames))
	co[0::2] = frames
	co[1::2] = values
	points.foreach_set('co', co)
	if len(frames) > 1:
		try:
			points.foreach_set('interpolation', [1] * len(frames))   # LINEAR
		except Exception:
			for point in points:
				point.interpolation = 'LINEAR'
	fcurve.update()

def _fcurve_factory(action, armature_object):
	# blender 4.4+ slotted actions, older versions Action.fcurves
	if hasattr(action, 'slots'):
		slot = action.slots.new('OBJECT', armature_object.name)
		layer = action.layers.new("Layer") if len(action.layers) == 0 else action.layers[0]
		strip = layer.strips.new(type='KEYFRAME') if len(layer.strips) == 0 else layer.strips[0]
		channelbag = strip.channelbag(slot, ensure=True)
		def new_fcurve(data_path, index, group):
			return channelbag.fcurves.new(data_path, index=index, group_name=group)
		return new_fcurve, slot
	else:
		def new_fcurve(data_path, index, group):
			return action.fcurves.new(data_path, index=index, action_group=group)
		return new_fcurve, None

# .anim file: see docs/FORMAT.md
ANIM_MAGIC = b'OVLANIM2'

def write_anim_file(action, writer):
	writer.write_string(ANIM_MAGIC)
	writer.write_float32([action.fps])
	writer.write_uint32([action.duration_us])
	writer.write_int32([len(action.bone_list)])
	for bone in action.bone_list:
		name = bone.name.encode('utf-8')
		writer.write_int32([len(name)])
		writer.write_string(name)
		writer.write_int32([len(bone.position_keys)])
		for time_us, (x, y, z) in bone.position_keys:
			writer.write_uint32([time_us])
			writer.write_float32([x, y, z])
		writer.write_int32([len(bone.raw_rotation)])
		writer.write_uint8([ROT_TYPE_QUAT_XYZ])
		for raw in bone.raw_rotation:
			writer.write_string(raw)
		sign_bytes = (len(bone.raw_rotation) + 7) // 8
		signs = bytes(bone.raw_signs[:sign_bytes]) + b'\x00' * max(0, sign_bytes - len(bone.raw_signs))
		writer.write_string(signs)

def read_anim_file(reader, name):
	magic = reader.read(8)
	if magic != ANIM_MAGIC:
		raise ValueError('Not an OVLANIM2 file (old .anim exports must be re-extracted from the .prp file)')
	action = Action()
	action.name = name
	action.fps = reader.read_float32(1)[0]
	action.duration_us = reader.read_uint32(1)[0]
	bone_count = reader.read_int32(1)[0]
	for m in range(bone_count):
		bone = ActionBone()
		bone.name = reader.read_string(reader.read_int32(1)[0])
		count = reader.read_int32(1)[0]
		for k in range(count):
			time_us = reader.read_uint32(1)[0]
			bone.position_keys.append((time_us, tuple(reader.read_float32(3))))
		count = reader.read_int32(1)[0]
		rot_type = reader.read_uint8(1)[0]
		if rot_type == ROT_TYPE_QUAT_XYZ:
			records = [reader.read(6) for k in range(count)]
			signs = reader.read((count + 7) // 8)
			bone.decode_rotation(records, signs)
		else:
			raise ValueError('Unsupported rotation type %d' % rot_type)
		action.bone_list.append(bone)
	return action
