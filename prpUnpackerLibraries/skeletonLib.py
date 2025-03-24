import bpy
import math
from mathutils import Matrix, Vector

class Bone:
	def __init__(self):
		self.name = None
		self.parent_id = None
		self.matrix = None

class Skeleton:
	def __init__(self):
		self.name = 'armature'
		self.bone_list = []
		self.armature = None
		self.object = None
		self.matrix = None

	def draw(self):
		self.check()
		if len(self.bone_list) > 0:
			self.create_bones()
			self.create_bone_connection()
			self.create_bone_position()

	def create_bones(self):
		bpy.context.view_layer.objects.active = self.object
		self.object.select_set(True)
		bpy.ops.object.mode_set(mode='EDIT')
		armature = self.object.data
		bone_list = [bone.name for bone in armature.edit_bones]
		for boneID in range(len(self.bone_list)):
			name = self.bone_list[boneID].name
			if name is None:
				name = str(boneID)
				self.bone_list[boneID].name = name
			if name not in bone_list:
				eb = armature.edit_bones.new(name)
				eb.head = (0, 0, 0)
				eb.tail = (0, 0, 1)
		bpy.ops.object.mode_set(mode='OBJECT')

	def create_bone_connection(self):
		bpy.context.view_layer.objects.active = self.object
		self.object.select_set(True)
		bpy.ops.object.mode_set(mode='EDIT')
		armature = self.object.data
		for boneID in range(len(self.bone_list)):
			name = self.bone_list[boneID].name
			if name is None:
				name = str(boneID)
			bone = armature.edit_bones.get(name)
			parent_id=None
			parent_name=None
			if self.bone_list[boneID].parent_id is not None:
				parent_id = self.bone_list[boneID].parent_id
				if parent_id != -1:
					parent_name = self.bone_list[parent_id].name
			if parent_name is not None:
				parent = armature.edit_bones.get(parent_name)
				if parent_id is not None:
					if parent_id != -1:
						bone.parent = parent
				else:
					print(f"Warning: Parent bone '{parent_name}' not found for bone '{name}'.")
			else:
				if name.lower() != "root":
					print(f"Warning: No parent for bone '{name}'.")
		bpy.ops.object.mode_set(mode='OBJECT')

	def create_bone_position(self):
		bpy.context.view_layer.objects.active = self.object
		self.object.select_set(True)
		bpy.ops.object.mode_set(mode='EDIT')
		armature = self.object.data

		world_matrices = {}

		for boneID in range(len(self.bone_list)):
			bone_data = self.bone_list[boneID]
			name = bone_data.name
			matrix = bone_data.matrix

			if name is None or matrix is None:
				print(f"NEW - WARNING: Missing data for bone '{name}'.")
				continue

			bone = armature.edit_bones.get(name)
			if not bone:
				print(f"WARNING: Bone '{name}' not found.")
				continue

			local_matrix = matrix.transposed()

			if bone.parent:
				parent_matrix = world_matrices.get(bone.parent.name)
				if not parent_matrix:
					continue
				world_matrix = parent_matrix @ local_matrix
			else:
				world_matrix = local_matrix.copy()

			world_matrices[name] = world_matrix

			bone.head = world_matrix.to_translation()

			y_axis = world_matrix.col[1].to_3d().normalized()
			bone.tail = bone.head + y_axis * 0.01

			# *** Roll Calculation Using AxisRollFromMatrix ***
			# Convert the world_matrix to a 3x3 rotation matrix.
			rot_mat = world_matrix.to_3x3()
			# Use the bone’s local Y axis from the rotation matrix as the reference axis.
			ref_axis = Vector((rot_mat[0][1], rot_mat[1][1], rot_mat[2][1])).normalized()
			# Compute the roll from the rotation matrix.
			# The function returns (computed_axis, roll)
			computed_axis, roll = bpy.types.Bone.AxisRollFromMatrix(rot_mat, axis=ref_axis)
			bone.roll = roll

		bpy.ops.object.mode_set(mode='OBJECT')

	def check(self):
		if self.object is None or self.object.name not in bpy.data.objects:
			bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
			self.object = bpy.context.object
			self.object.name = self.name
			self.armature = self.object.data
		if self.object.name not in bpy.context.scene.objects:
			bpy.context.scene.collection.objects.link(self.object)
		bpy.context.view_layer.objects.active = self.object
		self.object.select_set(True)
		bpy.ops.object.mode_set(mode='EDIT')
		for bone in self.armature.edit_bones:
			self.armature.edit_bones.remove(bone)
		bpy.ops.object.mode_set(mode='OBJECT')
		self.armature.display_type = 'STICK'
		self.object.show_in_front = True
		self.matrix = self.object.matrix_world