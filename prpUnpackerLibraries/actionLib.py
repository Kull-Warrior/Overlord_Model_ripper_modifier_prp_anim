import bpy
import Blender

class ActionBone:
	def	__init__(self):
		self.name=None
		self.position_frame_list=[]
		self.rotation_frame_list=[]
		self.scale_frame_list=[]
		self.position_key_list=[]
		self.rotation_key_list=[]
		self.scale_key_list=[]
		self.matrix_frame_list=[]
		self.matrix_key_list=[]
		self.data=[]

class Action:
	def __init__(self):
		self.frame_count=None
		self.name='action'
		self.skeleton='armature'
		self.bone_list=[]
		self.armature_space=False
		self.bone_space=False
		self.frame_sort=False
		self.bone_sort=False

	def bone_name_list(self):
		if self.skeleton is not None:
			scene = bpy.data.scenes.active
			for object in scene.objects:
				if object.name==self.skeleton:
					self.bone_name_list=object.getData().bones.keys()

	def set_context(self):
		scn = Blender.Scene.GetCurrent()
		context = scn.getRenderingContext()
		if self.frame_count is not None:
			context.eFrame = self.frame_count

	def draw(self):
		scene = bpy.data.scenes.active
		skeleton=None
		if self.skeleton is not None:
			for object in scene.objects:
				if object.getType()=='Armature':
					if object.name==self.skeleton:
						skeleton = object
		else:
			print 'Warning: no armature'
		if skeleton is not None:
			armature=skeleton.getData()
			pose = skeleton.getPose()
			action = Blender.Armature.NLA.NewAction(self.name)
			action.setActive(skeleton)
			scn = Blender.Scene.GetCurrent()
			timeList=[]

			if self.frame_sort is True:
				frameList=[]
				for m in range(len(self.bone_list)):
					actionbone=self.bone_list[m]
					for n in range(len(actionbone.position_frame_list)):
						frame=actionbone.position_frame_list[n]
						if frame not in frameList:
							frameList.append(frame)
					for n in range(len(actionbone.rotation_frame_list)):
						frame=actionbone.rotation_frame_list[n]
						if frame not in frameList:
							frameList.append(frame)
					for n in range(len(actionbone.matrix_frame_list)):
						frame=actionbone.matrix_frame_list[n]
						if frame not in frameList:
							frameList.append(frame)

				for k in range(len(frameList)):
					frame=sorted(frameList)[k]
					for m in range(len(self.bone_list)):
						actionbone=self.bone_list[m]
						name=actionbone.name
						pbone=pose.bones[name]
						if pbone is not None:
							for n in range(len(actionbone.position_frame_list)):
								if frame==actionbone.position_frame_list[n]:
									timeList.append(frame)
									poskey=actionbone.position_key_list[n]
									bonematrix=poskey#TranslationMatrix(Vector(poskey))#.resize4x4()
									if self.armature_space is True:
										pbone.poseMatrix=bonematrix
										pbone.insertKey(skeleton, frame,\
											[Blender.Object.Pose.LOC],True)
										pose.update()
									if self.bone_space is True:
										if pbone.parent:
											pbone.poseMatrix=bonematrix*pbone.parent.poseMatrix
										else:
											pbone.poseMatrix=bonematrix
										pbone.insertKey(skeleton, frame,\
											[Blender.Object.Pose.LOC],True)

							for n in range(len(actionbone.rotation_frame_list)):
								if frame==actionbone.rotation_frame_list[n]:
									timeList.append(frame)
									rotkey=actionbone.rotation_key_list[n]
									bonematrix=rotkey
									if self.armature_space is True:
										pbone.poseMatrix=bonematrix
										pbone.insertKey(skeleton, frame,\
											[Blender.Object.Pose.ROT],True)
										pose.update()
									if self.bone_space is True:
										if pbone.parent:
											pbone.poseMatrix=bonematrix*pbone.parent.poseMatrix
										else:
											pbone.poseMatrix=bonematrix
										pbone.insertKey(skeleton, frame,\
											[Blender.Object.Pose.ROT],True)

							for n in range(len(actionbone.matrix_frame_list)):
								if frame==actionbone.matrix_frame_list[n]:
									timeList.append(frame)
									matrix=actionbone.matrix_key_list[n]
									if self.armature_space is True:
										pbone.poseMatrix=matrix
										pbone.insertKey(skeleton, 1+frame,\
											[Blender.Object.Pose.ROT,Blender.Object.Pose.LOC],True)
										pose.update()
									if self.bone_space is True:
										if pbone.parent:
											pbone.poseMatrix=matrix*pbone.parent.poseMatrix
										else:
											pbone.poseMatrix=skeleton.matrixWorld*matrix
										pbone.insertKey(skeleton, 1+frame,\
											[Blender.Object.Pose.ROT,Blender.Object.Pose.LOC],True)
										pose.update()

			elif self.bone_sort is True:

				for m in range(len(self.bone_list)):
					actionbone=self.bone_list[m]
					name=actionbone.name
					pbone=pose.bones[name]
					Blender.Window.RedrawAll()

					if pbone is not None:
						pbone.insertKey(skeleton,0,[Blender.Object.Pose.ROT,Blender.Object.Pose.LOC],True)
						pose.update()
						
						for n in range(len(actionbone.position_frame_list)):
							frame=actionbone.position_frame_list[n]
							timeList.append(frame)
							poskey=actionbone.position_key_list[n]
							bonematrix=poskey#TranslationMatrix(Vector(poskey))#.resize4x4()
							if self.armature_space is True:
								pbone.poseMatrix=bonematrix
								pbone.insertKey(skeleton, 1+frame,\
									[Blender.Object.Pose.LOC],True)
								pose.update()
							if self.bone_space is True:
								if pbone.parent:
									pbone.poseMatrix=bonematrix*pbone.parent.poseMatrix
								else:
									pbone.poseMatrix=bonematrix
								pbone.insertKey(skeleton, 1+frame,\
									[Blender.Object.Pose.LOC],True)
								pose.update()

						for n in range(len(actionbone.rotation_frame_list)):
							frame=actionbone.rotation_frame_list[n]
							timeList.append(frame)
							rotkey=actionbone.rotation_key_list[n]
							bonematrix=rotkey
							if self.armature_space is True:
								pbone.poseMatrix=bonematrix
								pbone.insertKey(skeleton, 1+frame,\
									[Blender.Object.Pose.ROT],True)
								pose.update()
							if self.bone_space is True:
								if pbone.parent:
									pbone.poseMatrix=bonematrix*pbone.parent.poseMatrix
								else:
									pbone.poseMatrix=bonematrix
								pbone.insertKey(skeleton, 1+frame,\
									[Blender.Object.Pose.ROT],True)
								pose.update()

						for n in range(len(actionbone.matrix_frame_list)):
							frame=actionbone.matrix_frame_list[n]
							timeList.append(frame)
							matrixkey=actionbone.matrix_key_list[n]
							bonematrix=matrixkey
							if self.armature_space is True:
								pbone.poseMatrix=skeleton.matrixWorld*bonematrix
								pbone.insertKey(skeleton, 1+frame,\
									[Blender.Object.Pose.ROT,Blender.Object.Pose.LOC],True)
								pose.update()
							if self.bone_space is True:
								if pbone.parent:
									pbone.poseMatrix=bonematrix*pbone.parent.poseMatrix
								else:
									pbone.poseMatrix=bonematrix
								pbone.insertKey(skeleton, 1+frame,\
									[Blender.Object.Pose.ROT,Blender.Object.Pose.LOC],True)
								pose.update()
			else:
				print 'Warning: missing bone_sort or frame_sort'
			if len(timeList)>0:
				self.frame_count=max(map(int,timeList))