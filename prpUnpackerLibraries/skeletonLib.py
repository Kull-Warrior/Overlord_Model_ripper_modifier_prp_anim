from myFunction import *
import Blender
from Blender.Mathutils import *
import bpy

class Bone:
	def __init__(self):
		self.ID=None
		self.name=None
		self.parent_id=None
		self.parent_name=None
		self.quat=None
		self.position=None
		self.matrix=None
		self.position_matrix=None
		self.rotation_matrix=None
		self.scale_matrix=None
		self.children=[]
		self.edit=None

class Skeleton:
	def __init__(self):
		self.name='armature'
		self.bone_list=[]
		self.armature=None
		self.object=None
		self.bone_name_list=[]
		self.armature_space=False
		self.bone_space=False
		self.DEL=True
		self.NICE=False
		self.IK=False
		self.matrix=None

	def draw(self):
		self.check()
		if len(self.bone_list)>0:
			self.create_bones()
			self.create_bone_connection()
			self.create_bone_position()
		if self.IK==True:
			self.armature.drawType=Blender.Armature.OCTAHEDRON
			for key in self.armature.bones.keys():
				bone=self.armature.bones[key]
				children=bone.children
				if len(children)==1:
					self.armature.makeEditable()
					ebone=self.armature.bones[bone.name]
					if ebone.tail!=children[0].head['armature_space']:
						ebone.tail=children[0].head['armature_space']
					self.armature.update()
			for key in self.armature.bones.keys():
				bone=self.armature.bones[key]
				children=bone.children
				if len(children)==1:
					self.armature.makeEditable()
					self.armature.bones[children[0].name].options=Blender.Armature.CONNECTED
					self.armature.update()
			if self.IK==True:
				self.armature.autoIK=True

	def create_bones(self):
		self.armature.makeEditable()
		bone_list=[]
		for bone in self.armature.bones.values():
			if bone.name not in bone_list:
				bone_list.append(bone.name)
		for boneID in range(len(self.bone_list)):
			name=self.bone_list[boneID].name
			if name is None:
				name=str(boneID)
				self.bone_list[boneID].name=name
			self.bone_name_list.append(name)
			if name not in bone_list:
				eb = Blender.Armature.Editbone()
				self.armature.bones[name] = eb
		self.armature.update()

	def create_bone_connection(self):
		self.armature.makeEditable()
		for boneID in range(len(self.bone_list)):
			name=self.bone_list[boneID].name
			if name is None:
				name=str(boneID)
			bone=self.armature.bones[name]
			parent_id=None
			parent_name=None
			if self.bone_list[boneID].parent_id is not None:
				parent_id=self.bone_list[boneID].parent_id
				if parent_id!=-1:
					parent_name=self.bone_list[parent_id].name
			if self.bone_list[boneID].parent_name is not None:
				parent_name=self.bone_list[boneID].parent_name
			if parent_name is not None:
				parent=self.armature.bones[parent_name]
				if parent_id is not None:
					if parent_id!=-1:
						bone.parent=parent
				else:
					bone.parent=parent
			else:
				if name.lower() != "root":
					print 'Warning: no parent for bone',name
		self.armature.update()

	def create_bone_position(self):
		self.armature.makeEditable()
		for m in range(len(self.bone_list)):
			name=self.bone_list[m].name
			rotation_matrix=self.bone_list[m].rotation_matrix
			position_matrix=self.bone_list[m].position_matrix
			scale_matrix=self.bone_list[m].scale_matrix
			matrix=self.bone_list[m].matrix
			bone = self.armature.bones[name]
			if matrix is not None:
				if self.armature_space==True:
					bone.matrix=matrix
					if self.NICE==True:
						bvec = bone.tail- bone.head
						bvec.normalize()
						bone.tail = bone.head + 0.01 * bvec
				elif self.bone_space==True:
					rotation_matrix=matrix.rotationPart()
					position_matrix=matrix.translationPart()
					if bone.parent:
						bone.head = position_matrix * bone.parent.matrix+bone.parent.head
						tempM = rotation_matrix * bone.parent.matrix 
						bone.matrix = tempM
					else:
						bone.head = position_matrix
						bone.matrix = rotation_matrix
					if self.NICE==True:
						bvec = bone.tail- bone.head
						bvec.normalize()
						bone.tail = bone.head + 0.01 * bvec
				else:
					print 'ARMATUREPACE or bone_space ?'
			elif rotation_matrix is not None and position_matrix is not None:
				if self.armature_space==True:
					rotation_matrix=round_matrix(rotation_matrix,4)
					position_matrix=round_matrix(position_matrix,4)
					bone.matrix=rotation_matrix*position_matrix
					if self.NICE==True:
						bvec = bone.tail- bone.head
						bvec.normalize()
						bone.tail = bone.head + 0.01 * bvec
				elif self.bone_space==True:
					rotation_matrix=round_matrix(rotation_matrix,4).rotationPart()
					position_matrix=round_matrix(position_matrix,4).translationPart()
					if bone.parent:
						bone.head = position_matrix * bone.parent.matrix+bone.parent.head
						tempM = rotation_matrix * bone.parent.matrix
						bone.matrix = tempM
					else:
						bone.head = position_matrix
						bone.matrix = rotation_matrix
					if self.NICE==True:
						bvec = bone.tail- bone.head
						bvec.normalize()
						bone.tail = bone.head + 0.01 * bvec
				else:
					print 'ARMATUREPACE or bone_space ?'
			else:
				print 'WARNINIG: rotation_matrix or position_matrix or matrix is None'

		self.armature.update()
		Blender.Window.RedrawAll()

	def check(self):
		scn = Blender.Scene.GetCurrent()
		scene = bpy.data.scenes.active
		for object in scene.objects:
			if object.getType()=='Armature':
				if object.name == self.name:
					scene.objects.unlink(object)
		for object in bpy.data.objects:
			if object.name == self.name:
				self.object = Blender.Object.Get(self.name)
				self.armature = self.object.getData()
				if self.DEL==True:
					self.armature.makeEditable()
					for bone in self.armature.bones.values():
						del self.armature.bones[bone.name]
					self.armature.update()
		if self.object==None:
			self.object = Blender.Object.New('Armature',self.name)
		if self.armature==None:
			self.armature = Blender.Armature.New(self.name)
			self.object.link(self.armature)
		scn.link(self.object)
		self.armature.drawType = Blender.Armature.STICK
		self.object.drawMode = Blender.Object.DrawModes.XRAY
		self.matrix=self.object.mat