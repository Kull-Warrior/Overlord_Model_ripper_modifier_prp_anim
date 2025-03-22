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

		for boneID in range(len(self.bone_list)):
			bone_data = self.bone_list[boneID]
			name = bone_data.name
			matrix = bone_data.matrix

			if name is None or matrix is None:
				print(f"WARNING: Missing data for bone '{name}'.")
				continue

			bone = armature.edit_bones.get(name)
			if not bone:
				print(f"WARNING: Bone '{name}' not found.")
				continue

			# Transpose the input matrix to match modern Blender's convention.
			matrix_transposed = matrix.transposed()

			# Extract translation (position) and rotation (as a 3x3 matrix).
			position = matrix_transposed.to_translation()
			rotation = matrix_transposed.to_3x3()

			## Use an offset vector of (0.01, 0, 0) because the old code
			## effectively produced a tail offset of 0.01 units along the X-axis.
			#offset_vector = Vector((0.01, 0, 0))
			#offset = rotation @ offset_vector  # Apply rotation to the offset

			#if bone.parent:
			#	# For child bones, the head should match the parent's tail.
			#	bone.head = bone.parent.tail
			#	bone.tail = bone.head + offset
			#	print(f"NEW - Bone '{name}' with parent '{bone.parent.name}':")
			#	print(f"       Parent Tail = {bone.parent.tail}")
			#	print(f"       Child Head  = {bone.head}")
			#	print(f"       Child Tail  = {bone.tail}")
			#else:
			#	# For a root bone, head is the transformed position.
			#	bone.head = position
			#	bone.tail = bone.head + offset
			#	print(f"NEW - Root Bone '{name}':")
			#	print(f"       Head = {bone.head}")
			#	print(f"       Tail = {bone.tail}")
			
			bone.head = position
			
			y_axis = matrix_transposed.col[1].to_3d().normalized()  # bone’s local Y axis
			bone_length = 0.01  # as desired
			bone.tail = bone.head + y_axis * bone_length
			
			rotation_matrix = matrix_transposed.to_3x3()
			roll_rad = rotation_matrix.to_euler('XYZ').y  # Extract the Z component (roll)
			bone.roll = roll_rad
			
			break

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