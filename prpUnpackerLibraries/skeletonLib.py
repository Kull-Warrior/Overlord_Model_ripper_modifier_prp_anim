import bpy
import math
from mathutils import Matrix, Vector, Quaternion

from myFunction import GAME_TO_BLENDER, game_matrix_to_blender

# bone custom properties, used when applying .anim files later on
PROP_REST_LOCAL = "ovl_rest_local"
PROP_ORIENT = "ovl_orient"

class Bone:
	def __init__(self):
		self.name = None
		self.parent_id = None
		self.skin_id = None
		self.matrix = None          # parent relative rest matrix, game space
		self.rest_local = None      # same in blender space
		self.rest_world = None
		self.orient = None          # extra rotation so the blender bone points at its child
		self.length = 0.1
		self.blender_name = None

class Skeleton:
	orient_bones_to_children = True

	def __init__(self):
		self.name = 'armature'
		self.bone_list = []
		self.armature = None
		self.object = None
		self.matrix = None
		self.collection = None

	def signature(self):
		parts = []
		for bone in self.bone_list:
			m = bone.matrix
			parts.append((bone.name, bone.parent_id, tuple(round(m[i][j], 4) for i in range(4) for j in range(4))))
		return hash(tuple(parts))

	def bone_names(self):
		return set(bone.name for bone in self.bone_list)

	def draw(self):
		self.check()
		if len(self.bone_list) > 0:
			self.compute_rest_pose()
			self.create_bones()

	def ordered_bones(self):
		ordered = []
		done = set()
		pending = list(self.bone_list)
		while pending:
			progress = False
			for bone in list(pending):
				parent = self.get_parent(bone)
				if parent is None or id(parent) in done:
					ordered.append(bone)
					done.add(id(bone))
					pending.remove(bone)
					progress = True
			if not progress:
				for bone in pending:
					bone.parent_id = -1
					ordered.append(bone)
				break
		return ordered

	def compute_rest_pose(self):
		children = {}
		for boneID, bone in enumerate(self.bone_list):
			if bone.name is None:
				bone.name = str(boneID)
		ordered = self.ordered_bones()
		for bone in ordered:
			bone.rest_local = game_matrix_to_blender(bone.matrix)
			parent = self.get_parent(bone)
			if parent is not None:
				bone.rest_world = parent.rest_world @ bone.rest_local
				children.setdefault(id(parent), []).append(bone)
			else:
				bone.rest_world = bone.rest_local.copy()

		for bone in ordered:
			parent = self.get_parent(bone)
			rotation = bone.rest_world.to_3x3()
			rotation.normalize()
			head = bone.rest_world.to_translation()

			direction = None
			length = None
			if self.orient_bones_to_children:
				for child in children.get(id(bone), []):
					d = child.rest_world.to_translation() - head
					if d.length > 1e-5:
						direction = d
						length = d.length
						break
				if direction is None and parent is not None:
					direction = parent.rest_world.to_3x3() @ parent.orient.to_3x3() @ Vector((0.0, 1.0, 0.0))
					length = parent.length * 0.5

			if direction is not None and direction.length > 1e-8:
				local_direction = rotation.inverted() @ direction
				bone.orient = Vector((0.0, 1.0, 0.0)).rotation_difference(local_direction).to_matrix().to_4x4()
			else:
				bone.orient = Matrix.Identity(4)
			if length is None or length < 1e-4:
				length = parent.length * 0.5 if parent is not None else 0.1
			bone.length = max(length, 1e-3)

	def get_parent(self, bone):
		if bone.parent_id is None or bone.parent_id < 0 or bone.parent_id >= len(self.bone_list):
			return None
		parent = self.bone_list[bone.parent_id]
		return parent if parent is not bone else None

	def create_bones(self):
		bpy.context.view_layer.objects.active = self.object
		self.object.select_set(True)
		bpy.ops.object.mode_set(mode='EDIT')
		armature = self.object.data
		for bone in self.bone_list:
			eb = armature.edit_bones.new(bone.name)
			bone.blender_name = eb.name
			rotation = bone.rest_world.to_3x3()
			rotation.normalize()
			head = bone.rest_world.to_translation()
			eb.head = head
			eb.tail = head + Vector((0.0, bone.length, 0.0))
			eb.length = bone.length
			eb.matrix = Matrix.Translation(head) @ (rotation.to_4x4() @ bone.orient)
		for bone in self.bone_list:
			parent = self.get_parent(bone)
			if parent is not None:
				armature.edit_bones[bone.blender_name].parent = armature.edit_bones[parent.blender_name]
			elif bone.name.lower() not in ("root", "dummy"):
				print(f"	Info: bone '{bone.name}' has no parent.")
		bpy.ops.object.mode_set(mode='OBJECT')

		for bone in self.bone_list:
			b = armature.bones[bone.blender_name]
			b[PROP_REST_LOCAL] = [bone.rest_local[i][j] for i in range(4) for j in range(4)]
			q = bone.orient.to_quaternion()
			b[PROP_ORIENT] = [q.w, q.x, q.y, q.z]
			pb = self.object.pose.bones[bone.blender_name]
			pb.rotation_mode = 'QUATERNION'

	def check(self):
		if self.object is None or self.object.name not in bpy.data.objects:
			self.armature = bpy.data.armatures.new(self.name)
			self.object = bpy.data.objects.new(self.name, self.armature)
			collection = self.collection if self.collection is not None else bpy.context.scene.collection
			collection.objects.link(self.object)
		if self.object.name not in bpy.context.view_layer.objects:
			bpy.context.scene.collection.objects.link(self.object)
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.view_layer.objects.active = self.object
		self.object.select_set(True)
		self.armature.display_type = 'STICK'
		self.object.show_in_front = True
		self.matrix = self.object.matrix_world

def bone_rest_data(armature_object, bone_name):
	bone = armature_object.data.bones.get(bone_name)
	if bone is None:
		return None, None
	orient = Matrix.Identity(4)
	if PROP_ORIENT in bone:
		w, x, y, z = bone[PROP_ORIENT]
		orient = Quaternion((w, x, y, z)).to_matrix().to_4x4()
	if PROP_REST_LOCAL in bone:
		v = list(bone[PROP_REST_LOCAL])
		rest_local = Matrix([v[i:i+4] for i in range(0, 16, 4)])
	else:
		rest_local = bone.matrix_local.copy()
		if bone.parent is not None:
			rest_local = bone.parent.matrix_local.inverted() @ rest_local
	return rest_local, orient
