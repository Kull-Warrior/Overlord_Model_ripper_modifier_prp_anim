import bpy
from mathutils import Matrix, Vector

class Bone:
	def __init__(self):
		self.ID = None
		self.name = None
		self.parent_id = None
		self.parent_name = None
		self.quat = None
		self.position = None
		self.matrix = None
		self.position_matrix = None
		self.rotation_matrix = None
		self.scale_matrix = None
		self.children = []
		self.edit = None


class Skeleton:
	def __init__(self):
		self.name = 'armature'
		self.bone_list = []
		self.armature = None
		self.object = None
		self.bone_name_list = []
		self.armature_space = False
		self.bone_space = False
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
			self.bone_name_list.append(name)
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
			if bone:
				parent_id = self.bone_list[boneID].parent_id
				parent_name = self.bone_list[boneID].parent_name
				if parent_id is not None and parent_id != -1:
					parent_name = self.bone_list[parent_id].name
				if parent_name:
					parent = armature.edit_bones.get(parent_name)
					if parent:
						bone.parent = parent
					else:
						print(f"Warning: Parent bone '{parent_name}' not found for bone '{name}'.")
				elif name.lower() != "root":
					print(f"Warning: No parent for bone '{name}'.")
		bpy.ops.object.mode_set(mode='OBJECT')

	def create_bone_position(self):
		bpy.context.view_layer.objects.active = self.object
		self.object.select_set(True)
		bpy.ops.object.mode_set(mode='EDIT')
		armature = self.object.data
		
		for m in range(len(self.bone_list)):
			name = self.bone_list[m].name
			bone = armature.edit_bones.get(name)
			if not bone:
				continue

			# Get matrices from bone data
			rotation = self.bone_list[m].rotation_matrix
			position = self.bone_list[m].position_matrix
			matrix = self.bone_list[m].matrix

			if matrix is not None:
				if self.armature_space:
					# Use full 4x4 matrix directly
					bone.matrix = matrix

				elif self.bone_space:
					# Construct 4x4 matrix from components
					if rotation and position:
						# Convert 3x3 rotation to 4x4
						rot_matrix = rotation.to_4x4()
						# Create translation matrix
						trans_matrix = Matrix.Translation(position)
						bone.matrix = trans_matrix @ rot_matrix

				bone.tail = bone.head + Vector((0, 0, 0.01))

			elif rotation is not None and position is not None:
				if self.armature_space:
					# Combine rotation and position into 4x4
					bone.matrix = rotation.to_4x4() @ Matrix.Translation(position)

				elif self.bone_space:
					# Handle parent-relative transformation
					if bone.parent:
						parent_matrix = bone.parent.matrix
						bone.matrix = parent_matrix @ rotation.to_4x4()
						bone.head = parent_matrix @ position
					else:
						bone.matrix = rotation.to_4x4()
						bone.head = position

				bone.tail = bone.head + Vector((0, 0, 0.01))

			# Set bone tail based on rotation if not set
			if bone.head == bone.tail:
				bone.tail = bone.head + rotation @ Vector((0, 0, 0.1))

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.context.view_layer.update()

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


	def round_matrix(matrix, precision):
		for i in range(len(matrix)):
			for j in range(len(matrix[i])):
				matrix[i][j] = round(matrix[i][j], precision)
		return matrix