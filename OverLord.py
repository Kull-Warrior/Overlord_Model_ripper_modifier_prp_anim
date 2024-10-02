import prpUnpackerLibraries
reload(prpUnpackerLibraries)
from prpUnpackerLibraries import *
import Blender
import math
from math import *
import struct

def get_item(list,ID):
	listA=[]
	for item in list:
		if item[0]==ID:
			listA.append(item)
	return listA

def get_list(type,list_reader):
	list=[]
	if type>=128:
		count_small=type-128
		count_big=list_reader.read_int32(1)[0]
		for m in range(count_small):
			list.append(list_reader.read_uint8(2))
		for m in range(count_big):
			list.append(list_reader.read_int32(2))
	else:
		count_small=type
		for m in range(count_small):
			list.append(list_reader.read_uint8(2))
	position=list_reader.tell()
	listA=[]
	for item in list:
		listA.append([item[0],position+item[1]])
	return listA

def prp_file_parser(filename,prp_reader):
	texture_list={}
	image_list=[]
	material_list=[]
	mesh_list=[]
	model_list=[]
	skeleton_list=[]
	action_list=[]
	audio_list=[]

########################################################################################################################################################################
## Read data from prp file
########################################################################################################################################################################

	title=get_title(prp_reader)
	print 'Title : ',title
	type=prp_reader.read_uint8(1)[0]
	print 'type : ',type
	list=get_list(type,prp_reader)
	list26=get_item(list,26)
	for item in list26:
		prp_reader.seek(item[1])
		prp_reader.read_uint8(3)
		type1=prp_reader.read_uint8(1)[0]
		list1=get_list(type1,prp_reader)
		for item1 in list1:
			prp_reader.seek(item1[1])
			flag=prp_reader.read_uint8(4)

			if flag in [(61,0,65,0),(153,0,65,0),(152,0,65,0)]:#image
				type2=prp_reader.read_uint8(1)[0]
				list2=get_list(type2,prp_reader)
				for item2 in list2:
					prp_reader.seek(item2[1])
					if item2[0]==20:
						texture_chunk=prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==21:
						texture_name=prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==1:
						type3=prp_reader.read_uint8(1)[0]
						list3=get_list(type3,prp_reader)
						for item3 in list3:
							prp_reader.seek(item3[1])
							if item3[0]==20:
								prp_reader.read_uint8(3)
								type4=prp_reader.read_uint8(1)[0]
								list4=get_list(type4,prp_reader)
								for item4 in list4:
									prp_reader.seek(item4[1])
									flag=prp_reader.read_uint8(4)
									if flag==(36,0,65,0):
										type5=prp_reader.read_uint8(1)[0]
										list5=get_list(type5,prp_reader)
										image=imageLib.Image()
										for item5 in list5:
											prp_reader.seek(item5[1])
											if item5[0]==20:
												image.width=prp_reader.read_int32(1)[0]
											if item5[0]==21:
												image.height=prp_reader.read_int32(1)[0]
											if item5[0]==23:
												format=prp_reader.read_int32(1)[0]
											if item5[0]==22:
												offset=prp_reader.tell()
										prp_reader.seek(offset)
										image.format=set_image_format(format,image)
										
										#If no file extension could be read directly, it will be appended to the to be created file depending on the image type
										if '.' not in texture_name and 'DXT' in image.format:
											texture_name=texture_name+".dds"
										elif '.' not in texture_name and 'tga' in image.format:
											texture_name=texture_name+".tga"
										
										image.name=file_directory+os.sep+file_basename+os.sep+'images'+os.sep+texture_name
										image.data=prp_reader.read(image.width*image.height*4)
										image_list.append(image)
										texture_list[texture_chunk]=image.name
										break
									else:
										print 'unknow image flag:',flag,prp_reader.tell()

			elif flag==(5,0,65,0):#anim
				action=Action()

				type2=prp_reader.read_uint8(1)[0]
				list2=get_list(type2,prp_reader)

				list21=get_item(list2,21)
				for item21 in list21:
					prp_reader.seek(item21[1])
					action.name=prp_reader.read_word(prp_reader.read_int32(1)[0])

				list1=get_item(list2,1)
				for item1 in list1:
					prp_reader.seek(item1[1])
					type3=prp_reader.read_uint8(1)[0]
					list3=get_list(type3,prp_reader)
					list10=get_item(list3,10)
					for item10 in list10:
						prp_reader.seek(item10[1])
						prp_reader.read_uint8(3)
						type4=prp_reader.read_uint8(1)[0]
						list4=get_list(type4,prp_reader)
						for item4 in list4:
							prp_reader.seek(item4[1])
							flag=prp_reader.read_uint8(4)
							if flag==(7,0,65,0):#anim
								type5=prp_reader.read_uint8(1)[0]
								list5=get_list(type5,prp_reader)
								action_bone=ActionBone()
								for item5 in list5:
									prp_reader.seek(item5[1])
									if item5[0]==20:
										action_bone.name=prp_reader.read_word(prp_reader.read_int32(1)[0])
									if item5[0]==24:
										position_frame_count=None
										position_stream_offset=None
										type6=prp_reader.read_uint8(1)[0]
										list6=get_list(type6,prp_reader)
										for item6 in list6:
											prp_reader.seek(item6[1])
											if item6[0]==21:
												position_frame_count=prp_reader.read_int32(1)[0]
											if item6[0]==22:
												position_stream_offset=prp_reader.tell()
										if (position_frame_count and position_stream_offset) is not None:
											prp_reader.seek(position_stream_offset)
											action_bone.data.append(struct.pack('<'+'i',position_frame_count))
											for mC in range(position_frame_count):
												prp_reader.seek(2,1)
												position_data=prp_reader.read(14)
												action_bone.data.append(position_data)
										else:
											action_bone.data.append(struct.pack('<'+'i',0))
											

									if item5[0]==25:

										scale_frame_count=None
										scale_stream_offset=None

										rotation_frame_count=None
										rotation_stream_offset=None
										type6=prp_reader.read_uint8(1)[0]
										list6=get_list(type6,prp_reader)
										for item6 in list6:
											prp_reader.seek(item6[1])
											if item6[0]==21:
												type7=prp_reader.read_uint8(1)[0]
												list7=get_list(type7,prp_reader)
												for item7 in list7:
													prp_reader.seek(item7[1])
													if item7[0]==22:
														rotation_frame_count=prp_reader.read_int32(1)[0]
													if item7[0]==23:
														rotation_stream_offset=prp_reader.tell()
													if item7[0]==30:
														scale_frame_count=prp_reader.read_int32(1)[0]
													if item7[0]==31:
														scale_stream_offset=prp_reader.tell()
										if (rotation_frame_count and rotation_stream_offset) is not None:
											prp_reader.seek(rotation_stream_offset)
											action_bone.data.append(struct.pack('<'+'i',rotation_frame_count))
											action_bone.data.append(struct.pack('<'+'B',22))
											for mC in range(rotation_frame_count):
												rotation_data=prp_reader.read(6)
												action_bone.data.append(rotation_data)

										elif (scale_frame_count and scale_stream_offset) is not None:
											prp_reader.seek(scale_stream_offset)
											action_bone.data.append(struct.pack('<'+'i',scale_frame_count))
											action_bone.data.append(struct.pack('<'+'B',30))
											for mC in range(scale_frame_count):
												scale_data=prp_reader.read(8)
												action_bone.data.append(scale_data)
										else:
											action_bone.data.append(struct.pack('<'+'i',0))
											action_bone.data.append(struct.pack('<'+'B',0))
								action.bone_list.append(action_bone)
				action_list.append(action)

			elif flag==(53,0,65,0):#mesh
				mesh=Mesh()
				mesh_list.append(mesh)
				type2=prp_reader.read_uint8(1)[0]
				list2=get_list(type2,prp_reader)
				for item2 in list2:
					prp_reader.seek(item2[1])
					if item2[0]==20:
						mesh.chunk=prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==21:
						mesh.name=prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==1:
						type3=prp_reader.read_uint8(1)[0]
						list3=get_list(type3,prp_reader)
						for item3 in list3:
							prp_reader.seek(item3[1])
							if item3[0]==10:
								type4=prp_reader.read_uint8(1)[0]
								list4=get_list(type4,prp_reader)
								indice_count=None
								for item4 in list4:
									prp_reader.seek(item4[1])
									if item4[0]==21:
										indice_count=prp_reader.read_int32(1)[0]
									if item4[0]==22:
										indice_offset=prp_reader.tell()
								if indice_count is not None:
									mesh.indice_list=prp_reader.read_uint16(indice_count)
									mesh.is_triangle=True
									mesh.matrix=Euler(90,0,0).toMatrix().resize4x4()

							if item3[0]==21:
								type4=prp_reader.read_uint8(1)[0]
								list4=get_list(type4,prp_reader)
								indice_count=None
								for item4 in list4:
									prp_reader.seek(item4[1])
									if item4[0]==21:
										indice_count=prp_reader.read_int32(1)[0]
									if item4[0]==22:
										indice_offset=prp_reader.tell()

								if indice_count is not None:
									mesh.indice_list=prp_reader.read_uint16(indice_count)
									mesh.is_triangle_strip=True

							if item3[0]==11:
								type4=prp_reader.read_uint8(1)[0]
								list4=get_list(type4,prp_reader)
								for item4 in list4:
									prp_reader.seek(item4[1])
									if item4[0]==20:
										type5=prp_reader.read_uint8(1)[0]
										list5=get_list(type5,prp_reader)
										for item5 in list5:
											prp_reader.seek(item5[1])
											if item5[0]==21:
												vertice_stride_size=prp_reader.read_int32(1)[0]
											if item5[0]==22:
												vertice_item_count=prp_reader.read_int32(1)[0]
											if item5[0]==23:
												vertice_item_offset=prp_reader.tell()
										prp_reader.seek(vertice_item_offset)
										vertice_position_offset=None
										vertice_uv_offset=None
										skin_indice_offset=None
										skin_weight_offset=None
										offset=0
										for k in range(vertice_item_count):
											a,b,c,d=prp_reader.read_uint8(4)
											if c==1:vertice_position_offset=offset
											if c==5 and a==0:
												vertice_uv_offset=offset
											if c==11:skin_indice_offset=offset
											if c==10:skin_weight_offset=offset
											if d==2:offset+=12
											if d==1:offset+=8
											if d==3:offset+=16
											if d==4:offset+=1
											if d==7:offset+=1
											if d==15:offset+=4
									if item4[0]==21:
										vertice_count=prp_reader.read_int32(1)[0]
									if item4[0]==21:
										stream_offset=prp_reader.tell()
				prp_reader.seek(stream_offset)
				for k in range(vertice_count):
					tk=prp_reader.tell()
					if vertice_position_offset is not None:
						prp_reader.seek(tk+vertice_position_offset)
						mesh.vertice_position_list.append(prp_reader.read_float(3))
					if vertice_uv_offset is not None:
						prp_reader.seek(tk+vertice_uv_offset)
						mesh.vertice_uv_list.append(prp_reader.read_float(2))
					if skin_indice_offset is not None:
						i1,i2,i3=prp_reader.read_uint8(3)
						mesh.skin_indice_list.append([i1,i2])
					if skin_weight_offset is not None:
						w1,w2=prp_reader.read_uint8(2)
						w3=255-(w1+w2)
						mesh.skin_weight_list.append([w1,w2])
					prp_reader.seek(tk+vertice_stride_size)

			elif flag in [(82,6,65,0),(60,6,65,0),(36,6,65,0),(10,6,65,0),(15,6,65,0),(8,6,65,0),(54,6,65,0),(38,6,65,0),(18,6,65,0),(22,6,65,0),(32,6,65,0),(50,6,65,0),(55,6,65,0),(48,6,65,0),(86,6,65,0),(49,6,65,0),(89,6,65,0)]:#material
				type2=prp_reader.read_uint8(1)[0]
				list2=get_list(type2,prp_reader)
				material=Mat()
				material.diffChunk=None
				material_list.append(material)
				for item2 in list2:
					prp_reader.seek(item2[1])
					if item2[0]==20:
						material.chunk=prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==21:
						material.name=prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==30:
						type3=prp_reader.read_uint8(1)[0]
						list3=get_list(type3,prp_reader)
						for item3 in list3:
							prp_reader.seek(item3[1])
							if item3[0]==20:
								chunk=prp_reader.read_word(prp_reader.read_int32(1)[0])
								material.diffChunk=chunk
							if item3[0]==21:
								material.texture_file=prp_reader.read_word(prp_reader.read_int32(1)[0])

			elif flag in [(75,0,65,0)]:#model
				model=Model()
				model_list.append(model)
				type2=prp_reader.read_uint8(1)[0]
				list2=get_list(type2,prp_reader)
				for item2 in list2:
					prp_reader.seek(item2[1])
					if item2[0]==20:
						model.chunk=prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==21:
						model.name=prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==30:
						type3=prp_reader.read_uint8(1)[0]
						list3=get_list(type3,prp_reader)
						for item3 in list3:
							prp_reader.seek(item3[1])
							if item3[0]==1:
								type4=prp_reader.read_uint8(1)[0]
								list4=get_list(type4,prp_reader)
								for item4 in list4:
									prp_reader.seek(item4[1])
									flag=prp_reader.read_uint8(4)
									if flag==(103,0,65,0):
										type5=prp_reader.read_uint8(1)[0]
										list5=get_list(type5,prp_reader)
										mesh_chunk,material_Chunk=None,None
										for item5 in list5:
											prp_reader.seek(item5[1])
											if item5[0]==31:
												type6=prp_reader.read_uint8(1)[0]
												list6=get_list(type6,prp_reader)
												for item6 in list6:
													prp_reader.seek(item6[1])
													if item6[0]==20:
														chunk=prp_reader.read_word(prp_reader.read_int32(1)[0])
														mesh_chunk=chunk
											if item5[0]==33:
												type6=prp_reader.read_uint8(1)[0]
												list6=get_list(type6,prp_reader)
												for item6 in list6:
													prp_reader.seek(item6[1])
													if item6[0]==20:
														chunk=prp_reader.read_word(prp_reader.read_int32(1)[0])
														material_Chunk=chunk
										if (mesh_chunk and material_Chunk) is not None:
											model.mesh_list.append([mesh_chunk,material_Chunk])
					if item2[0]==33:
						type3=prp_reader.read_uint8(1)[0]
						list3=get_list(type3,prp_reader)
						bone_count=None
						for item3 in list3:
							prp_reader.seek(item3[1])
							if item3[0]==20:
								prp_reader.read_int32(1)[0]
							if item3[0]==21:
								bone_count=prp_reader.read_int32(1)[0]
							if item3[0]==22:
								stream_offset=prp_reader.tell()
						if bone_count is not None and safe(bone_count):
							skeleton=Skeleton()
							skeleton.bone_space=True
							skeleton.NICE=True
							skeleton.name=model.name
							for m in range(bone_count):
								tm=prp_reader.tell()
								bone=Bone()
								bone.name=prp_reader.read_word(32)
								bone.matrix=matrix_4x4(prp_reader.read_float(16))
								prp_reader.read_float(4)
								prp_reader.read_float(3)
								a,b,c,d,e=prp_reader.read_int32(5)
								bone.parent_id=b
								bone.skinID=a
								model.bone_name_list.append(bone.name)
								skeleton.bone_list.append(bone)
								prp_reader.seek(tm+144)
							model.skeleton=skeleton.name
							for m in range(bone_count):
								model.bone_name_list[skeleton.bone_list[m].skinID]=skeleton.bone_list[m].name
							
							skeleton_list.append(skeleton)
					if item2[0]==35:
						type3=prp_reader.read_uint8(1)[0]
						list3=get_list(type3,prp_reader)
						bone_count=None
						for item3 in list3:
							prp_reader.seek(item3[1])
							if item3[0]==1:
								type4=prp_reader.read_uint8(1)[0]
								list4=get_list(type4,prp_reader)
								for item4 in list4:
									prp_reader.seek(item4[1])
									flag=prp_reader.read_uint8(4)
									if flag==(160,0,65,0):
										type5=prp_reader.read_uint8(1)[0]
										list5=get_list(type5,prp_reader)
										count=None
										for item5 in list5:
											prp_reader.seek(item5[1])
											if item5[0]==22:
												count=prp_reader.read_int32(1)[0]
											if item5[0]==23:
												stream_offset=prp_reader.tell()
										if count is not None:
											prp_reader.seek(stream_offset)
											model.bone_map_list.append(prp_reader.read_int32(count))

			elif flag == (0,0,161,0):
				type2=prp_reader.read_uint8(1)[0]
				list2=get_list(type2,prp_reader)
				
				audio=Audio()
				
				for item2 in list2:
					prp_reader.seek(item2[1])
					
					if item2[0]==20:
						audio.chunk_name = prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==21:
						audio.name=prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==100:
						audio.temp_path=prp_reader.read_word(prp_reader.read_int32(1)[0])
					if item2[0]==1:
						type3=prp_reader.read_uint8(1)[0]
						list3=get_list(type3,prp_reader)
						for item3 in list3:
							prp_reader.seek(item3[1])
							if item3[0] == 30:
								prp_reader.seek(item3[1])
								audio.size = prp_reader.read_uint32(1)[0]
							if item3[0] == 31:
								audio.data = prp_reader.read(audio.size)

				audio_list.append(audio)
			elif flag in [(27,6,65,0),(40,6,65,0),(42,6,65,0)]:#Final Gather Map ( Not implemented / not supported)
				pass
			elif flag == (17, 1, 65, 0):#COL Data ( Not implemented / not supported)
				pass
			elif flag == (0, 21, 65, 0):#INTERFACETEXTUREATLAS ( Not implemented / not supported)
				pass
			elif flag == (39, 160, 0, 4):#Unknown Data, something with alphabetical letters
				pass
			elif flag == (40, 160, 0, 4):#CliffData ( Not implemented / not supported)
				pass
			else:
				print 'unknow global flag:',flag,prp_reader.tell()

########################################################################################################################################################################
## Write necessary data to new files
########################################################################################################################################################################
	
	if len(image_list)>0 or len(action_list)>0 or len(audio_list)>0:
		create_new_directory(file_directory+os.sep+file_basename)
	
	if len(image_list)>0:
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'images')

	for image in image_list:
		image.draw()
	
	if len(action_list)>0:
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'animations')
	
	for action in action_list:
		animation_path=file_directory+os.sep+file_basename+os.sep+'animations'+os.sep+action.name+'.anim'
		animation_file=open(animation_path,'wb')
		animation_writer=BinaryReader(animation_file)
		
		for action_bone in action.bone_list:
			animation_writer.write_word(action_bone.name)
			animation_writer.write_word('\x00')
			
			for i in action_bone.data:
				animation_writer.write_word(i)
	
	if len(audio_list)>0:
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'audio')
	
	for audio in audio_list:
		audio_path=file_directory+os.sep+file_basename+os.sep+'audio'+os.sep+audio.name+'.wav'
		audio_file=open(audio_path,'wb')
		audio_writer=BinaryReader(audio_file)

		audio_writer.write_word(audio.data)

########################################################################################################################################################################
## Create blender models
########################################################################################################################################################################

	for skeleton in skeleton_list:
		skeleton.draw()

	for model in model_list:
		print '		model:',model.name
		i=0
		for mesh_chunk,material_Chunk in model.mesh_list:
			print '			',mesh_chunk, ' -> ', material_Chunk
			mat=None
			for mat in material_list:
				if mat.chunk==material_Chunk:
					break
			for mesh in mesh_list:
				if mesh.chunk==mesh_chunk:
					print '			Mesh Name	:	',mesh.name
					MAT=Mat()
					if mesh.is_triangle==True:MAT.is_triangle=True
					if mesh.is_triangle_strip==True:MAT.is_triangle_strip=True
					if mat is not None:

						if mat.diffChunk is not None:
							if mat.diffChunk in texture_list.keys():
								mat.diffuse=texture_list[mat.diffChunk]

						MAT.diffuse=mat.diffuse

					print '			Material Name	:	',MAT.name
					mesh.material_list.append(MAT)
					mesh.bone_name_list=model.bone_name_list
					if i<len(model.bone_map_list):
						skin=Skin()
						skin.bone_map=model.bone_map_list[i]
						mesh.skin_list.append(skin)

					mesh.bind_skeleton=model.skeleton
					try:
						mesh.draw()
					except:
						pass
					break
			i+=1

def anim_file_parser(filename,animation_reader):
	selObjectList=Blender.Object.GetSelected()
	if len(selObjectList)>0:
		armature=selObjectList[0]
		action=Action()
		action.skeleton=armature.name
		action.bone_space=True
		action.bone_sort=True
		action.UPDATE=False

		while(True):
			if animation_reader.tell()>=animation_reader.get_file_size():
				break
			bone=ActionBone()
			action.bone_list.append(bone)
			bone.name=animation_reader.find('\x00')
			count=animation_reader.read_int32(1)[0]
			for m in range(count):
				frame=animation_reader.read_uint16(1)[0]
				bone.position_frame_list.append(frame)
				bone.position_key_list.append(vector_matrix(animation_reader.read_float(3)))
			count=animation_reader.read_int32(1)[0]
			type=animation_reader.read_uint8(1)[0]
			if type==22:#not supported
				for m in range(count):
					bone.rotation_frame_list.append(m)
					x,y,z=animation_reader.short(3,'h',14)
					x=degrees(x)
					y=degrees(y)
					z=degrees(z)
					bone.rotation_key_list.append(Euler(x,y,z).toMatrix().resize4x4())
			if type==30:
				for m in range(count):
					bone.rotation_frame_list.append(m)
					bone.rotation_key_list.append(quat_matrix(animation_reader.short(4,'h',15)).resize4x4())

		action.draw()
		action.set_context()

def openFile(full_file_path):
	global file_directory,file_basename,file_extension
	file_directory=os.path.dirname(full_file_path)
	file_extension=os.path.basename(full_file_path).split('.')[-1]
	file_basename=os.path.basename(full_file_path).split('.'+file_extension)[0]

	print
	print '='*70
	print full_file_path
	print '='*70
	print

	if file_extension=='prp':
		file=open(full_file_path,'rb')
		reader=BinaryReader(file)
		prp_file_parser(full_file_path,reader)
		file.close()

	if file_extension=='anim':
		file=open(full_file_path,'rb')
		reader=BinaryReader(file)
		anim_file_parser(full_file_path,reader)
		file.close()

Blender.Window.FileSelector(openFile,'import','Overlord I and II files: prp - archive, anim - animation')