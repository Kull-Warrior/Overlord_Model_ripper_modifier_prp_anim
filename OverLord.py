import prpUnpackerLibraries
reload(prpUnpackerLibraries)
from prpUnpackerLibraries import *
import Blender
import math
from math import *
import struct

def read_data(filename):
	resource_file=open(filename,'rb')
	rpk_reader=BinaryReader(resource_file)

	image_count=0
	animation_count=0
	mesh_count=0
	material_count=0
	model_count=0
	audio_count=0
	final_gather_map_count=0
	color_count=0
	INTERFACETEXTUREATLAS_count=0
	alphabetical_data_count=0
	cliff_count=0
	shader_count=0

	########################################################################################################################################################################
	## Read data from a file with RPK structure
	########################################################################################################################################################################

	rpk_file=RPK()
	rpk_file.name=get_title(rpk_reader)
	print 'Title		:	',rpk_file.name
	rpk_file.type=rpk_reader.read_uint8(1)[0]

	list=get_list(rpk_file.type,rpk_reader)
	list26=get_item(list,26)
	for item in list26:
		rpk_reader.seek(item[1])
		rpk_reader.read_uint8(3)
		type1=rpk_reader.read_uint8(1)[0]
		list1=get_list(type1,rpk_reader)

		for item1 in list1:
			rpk_reader.seek(item1[1])
			flag=rpk_reader.read_uint8(4)

			if flag in [(61,0,65,0),(153,0,65,0),(152,0,65,0)]:#image
				image_count=image_count+1
				image=imageLib.Image()
				type2=rpk_reader.read_uint8(1)[0]
				list2=get_list(type2,rpk_reader)
				for item2 in list2:
					rpk_reader.seek(item2[1])
					if item2[0]==20:
						texture_chunk=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==21:
						image.name=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==1:
						type3=rpk_reader.read_uint8(1)[0]
						list3=get_list(type3,rpk_reader)
						for item3 in list3:
							rpk_reader.seek(item3[1])
							if item3[0]==20:
								rpk_reader.read_uint8(3)
								type4=rpk_reader.read_uint8(1)[0]
								list4=get_list(type4,rpk_reader)
								for item4 in list4:
									rpk_reader.seek(item4[1])
									flag=rpk_reader.read_uint8(4)
									if flag==(36,0,65,0):
										type5=rpk_reader.read_uint8(1)[0]
										list5=get_list(type5,rpk_reader)
										for item5 in list5:
											rpk_reader.seek(item5[1])
											if item5[0]==20:
												image.width=rpk_reader.read_int32(1)[0]
											if item5[0]==21:
												image.height=rpk_reader.read_int32(1)[0]
											if item5[0]==23:
												format=rpk_reader.read_int32(1)[0]
											if item5[0]==22:
												offset=rpk_reader.tell()
										rpk_reader.seek(offset)
										image.format=set_image_format(format,image)

										if '.' in image.name:
											image.name = image.name.split('.', 1)[0]

										#If no file extension could be read directly, it will be appended to the to be created file depending on the image type
										if '.' not in image.name and 'DXT' in image.format:
											image.name=image.name+".dds"
										elif '.' not in image.name and 'tga' in image.format:
											image.name=image.name+".tga"

										image.data=rpk_reader.read(image.width*image.height*4)
										rpk_file.image_list.append(image)
										rpk_file.texture_list[texture_chunk]=image.name
										break
									else:
										print 'unknow image flag:',flag,rpk_reader.tell()

			elif flag==(5,0,65,0):#anim
				animation_count=animation_count+1
				action=Action()

				type2=rpk_reader.read_uint8(1)[0]
				list2=get_list(type2,rpk_reader)

				list21=get_item(list2,21)
				for item21 in list21:
					rpk_reader.seek(item21[1])
					action.name=rpk_reader.read_word(rpk_reader.read_int32(1)[0])

				list1=get_item(list2,1)
				for item1 in list1:
					rpk_reader.seek(item1[1])
					type3=rpk_reader.read_uint8(1)[0]
					list3=get_list(type3,rpk_reader)
					list10=get_item(list3,10)
					for item10 in list10:
						rpk_reader.seek(item10[1])
						rpk_reader.read_uint8(3)
						type4=rpk_reader.read_uint8(1)[0]
						list4=get_list(type4,rpk_reader)
						for item4 in list4:
							rpk_reader.seek(item4[1])
							flag=rpk_reader.read_uint8(4)
							if flag==(7,0,65,0):#anim
								type5=rpk_reader.read_uint8(1)[0]
								list5=get_list(type5,rpk_reader)
								action_bone=ActionBone()
								for item5 in list5:
									rpk_reader.seek(item5[1])
									if item5[0]==20:
										action_bone.name=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
									if item5[0]==24:
										position_frame_count=None
										position_stream_offset=None
										type6=rpk_reader.read_uint8(1)[0]
										list6=get_list(type6,rpk_reader)
										for item6 in list6:
											rpk_reader.seek(item6[1])
											if item6[0]==21:
												position_frame_count=rpk_reader.read_int32(1)[0]
											if item6[0]==22:
												position_stream_offset=rpk_reader.tell()
										if (position_frame_count and position_stream_offset) is not None:
											rpk_reader.seek(position_stream_offset)
											action_bone.data.append(struct.pack('<'+'i',position_frame_count))
											for mC in range(position_frame_count):
												rpk_reader.seek(2,1)
												position_data=rpk_reader.read(14)
												action_bone.data.append(position_data)
										else:
											action_bone.data.append(struct.pack('<'+'i',0))
											

									if item5[0]==25:

										scale_frame_count=None
										scale_stream_offset=None

										rotation_frame_count=None
										rotation_stream_offset=None
										type6=rpk_reader.read_uint8(1)[0]
										list6=get_list(type6,rpk_reader)
										for item6 in list6:
											rpk_reader.seek(item6[1])
											if item6[0]==21:
												type7=rpk_reader.read_uint8(1)[0]
												list7=get_list(type7,rpk_reader)
												for item7 in list7:
													rpk_reader.seek(item7[1])
													if item7[0]==22:
														rotation_frame_count=rpk_reader.read_int32(1)[0]
													if item7[0]==23:
														rotation_stream_offset=rpk_reader.tell()
													if item7[0]==30:
														scale_frame_count=rpk_reader.read_int32(1)[0]
													if item7[0]==31:
														scale_stream_offset=rpk_reader.tell()
										if (rotation_frame_count and rotation_stream_offset) is not None:
											rpk_reader.seek(rotation_stream_offset)
											action_bone.data.append(struct.pack('<'+'i',rotation_frame_count))
											action_bone.data.append(struct.pack('<'+'B',22))
											for mC in range(rotation_frame_count):
												rotation_data=rpk_reader.read(6)
												action_bone.data.append(rotation_data)

										elif (scale_frame_count and scale_stream_offset) is not None:
											rpk_reader.seek(scale_stream_offset)
											action_bone.data.append(struct.pack('<'+'i',scale_frame_count))
											action_bone.data.append(struct.pack('<'+'B',30))
											for mC in range(scale_frame_count):
												scale_data=rpk_reader.read(8)
												action_bone.data.append(scale_data)
										else:
											action_bone.data.append(struct.pack('<'+'i',0))
											action_bone.data.append(struct.pack('<'+'B',0))
								action.bone_list.append(action_bone)
				rpk_file.animation_list.append(action)

			elif flag==(53,0,65,0):#mesh
				mesh_count=mesh_count+1
				mesh=Mesh()
				rpk_file.mesh_list.append(mesh)
				type2=rpk_reader.read_uint8(1)[0]
				list2=get_list(type2,rpk_reader)
				for item2 in list2:
					rpk_reader.seek(item2[1])
					if item2[0]==20:
						mesh.chunk=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==21:
						mesh.name=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==1:
						type3=rpk_reader.read_uint8(1)[0]
						list3=get_list(type3,rpk_reader)
						for item3 in list3:
							rpk_reader.seek(item3[1])
							if item3[0]==10:
								type4=rpk_reader.read_uint8(1)[0]
								list4=get_list(type4,rpk_reader)
								indice_count=None
								for item4 in list4:
									rpk_reader.seek(item4[1])
									if item4[0]==21:
										indice_count=rpk_reader.read_int32(1)[0]
									if item4[0]==22:
										indice_offset=rpk_reader.tell()
								if indice_count is not None:
									mesh.indice_list=rpk_reader.read_uint16(indice_count)
									mesh.is_triangle=True
									mesh.matrix=Euler(90,0,0).toMatrix().resize4x4()

							if item3[0]==21:
								type4=rpk_reader.read_uint8(1)[0]
								list4=get_list(type4,rpk_reader)
								indice_count=None
								for item4 in list4:
									rpk_reader.seek(item4[1])
									if item4[0]==21:
										indice_count=rpk_reader.read_int32(1)[0]
									if item4[0]==22:
										indice_offset=rpk_reader.tell()

								if indice_count is not None:
									mesh.indice_list=rpk_reader.read_uint16(indice_count)
									mesh.is_triangle_strip=True

							if item3[0]==11:
								type4=rpk_reader.read_uint8(1)[0]
								list4=get_list(type4,rpk_reader)
								for item4 in list4:
									rpk_reader.seek(item4[1])
									if item4[0]==20:
										type5=rpk_reader.read_uint8(1)[0]
										list5=get_list(type5,rpk_reader)
										for item5 in list5:
											rpk_reader.seek(item5[1])
											if item5[0]==21:
												vertice_stride_size=rpk_reader.read_int32(1)[0]
											if item5[0]==22:
												vertice_item_count=rpk_reader.read_int32(1)[0]
											if item5[0]==23:
												vertice_item_offset=rpk_reader.tell()
										rpk_reader.seek(vertice_item_offset)
										vertice_position_offset=None
										vertice_uv_offset=None
										skin_indice_offset=None
										skin_weight_offset=None
										offset=0
										for k in range(vertice_item_count):
											a,b,c,d=rpk_reader.read_uint8(4)
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
										vertice_count=rpk_reader.read_int32(1)[0]
									if item4[0]==21:
										stream_offset=rpk_reader.tell()
				rpk_reader.seek(stream_offset)
				for k in range(vertice_count):
					tk=rpk_reader.tell()
					if vertice_position_offset is not None:
						rpk_reader.seek(tk+vertice_position_offset)
						mesh.vertice_position_list.append(rpk_reader.read_float(3))
					if vertice_uv_offset is not None:
						rpk_reader.seek(tk+vertice_uv_offset)
						mesh.vertice_uv_list.append(rpk_reader.read_float(2))
					if skin_indice_offset is not None:
						i1,i2,i3=rpk_reader.read_uint8(3)
						mesh.skin_indice_list.append([i1,i2])
					if skin_weight_offset is not None:
						w1,w2=rpk_reader.read_uint8(2)
						w3=255-(w1+w2)
						mesh.skin_weight_list.append([w1,w2])
					rpk_reader.seek(tk+vertice_stride_size)

			elif flag in [(82,6,65,0),(60,6,65,0),(36,6,65,0),(10,6,65,0),(15,6,65,0),(8,6,65,0),(54,6,65,0),(38,6,65,0),(18,6,65,0),(22,6,65,0),(32,6,65,0),(50,6,65,0),(55,6,65,0),(48,6,65,0),(86,6,65,0),(49,6,65,0),(89,6,65,0)]:#material
				material_count=material_count+1
				type2=rpk_reader.read_uint8(1)[0]
				list2=get_list(type2,rpk_reader)
				material=Mat()
				material.diffChunk=None
				rpk_file.material_list.append(material)
				for item2 in list2:
					rpk_reader.seek(item2[1])
					if item2[0]==20:
						material.chunk=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==21:
						material.name=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==30:
						type3=rpk_reader.read_uint8(1)[0]
						list3=get_list(type3,rpk_reader)
						for item3 in list3:
							rpk_reader.seek(item3[1])
							if item3[0]==20:
								chunk=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
								material.diffChunk=chunk
							if item3[0]==21:
								material.texture_file=rpk_reader.read_word(rpk_reader.read_int32(1)[0])

			elif flag in [(75,0,65,0)]:#model
				model_count=model_count+1
				model=Model()
				rpk_file.model_list.append(model)
				type2=rpk_reader.read_uint8(1)[0]
				list2=get_list(type2,rpk_reader)
				for item2 in list2:
					rpk_reader.seek(item2[1])
					if item2[0]==20:
						model.chunk=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==21:
						model.name=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==30:
						type3=rpk_reader.read_uint8(1)[0]
						list3=get_list(type3,rpk_reader)
						for item3 in list3:
							rpk_reader.seek(item3[1])
							if item3[0]==1:
								type4=rpk_reader.read_uint8(1)[0]
								list4=get_list(type4,rpk_reader)
								for item4 in list4:
									rpk_reader.seek(item4[1])
									flag=rpk_reader.read_uint8(4)
									if flag==(103,0,65,0):
										type5=rpk_reader.read_uint8(1)[0]
										list5=get_list(type5,rpk_reader)
										mesh_chunk,material_Chunk=None,None
										for item5 in list5:
											rpk_reader.seek(item5[1])
											if item5[0]==31:
												type6=rpk_reader.read_uint8(1)[0]
												list6=get_list(type6,rpk_reader)
												for item6 in list6:
													rpk_reader.seek(item6[1])
													if item6[0]==20:
														chunk=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
														mesh_chunk=chunk
											if item5[0]==33:
												type6=rpk_reader.read_uint8(1)[0]
												list6=get_list(type6,rpk_reader)
												for item6 in list6:
													rpk_reader.seek(item6[1])
													if item6[0]==20:
														chunk=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
														material_Chunk=chunk
										if (mesh_chunk and material_Chunk) is not None:
											model.mesh_list.append([mesh_chunk,material_Chunk])
					if item2[0]==33:
						type3=rpk_reader.read_uint8(1)[0]
						list3=get_list(type3,rpk_reader)
						bone_count=None
						for item3 in list3:
							rpk_reader.seek(item3[1])
							if item3[0]==20:
								rpk_reader.read_int32(1)[0]
							if item3[0]==21:
								bone_count=rpk_reader.read_int32(1)[0]
							if item3[0]==22:
								stream_offset=rpk_reader.tell()
						if bone_count is not None and safe(bone_count):
							skeleton=Skeleton()
							skeleton.bone_space=True
							skeleton.NICE=True
							skeleton.name=model.name
							for m in range(bone_count):
								tm=rpk_reader.tell()
								bone=Bone()
								bone.name=rpk_reader.read_word(32)
								bone.matrix=matrix_4x4(rpk_reader.read_float(16))
								rpk_reader.read_float(4)
								rpk_reader.read_float(3)
								a,b,c,d,e=rpk_reader.read_int32(5)
								bone.parent_id=b
								bone.skinID=a
								model.bone_name_list.append(bone.name)
								skeleton.bone_list.append(bone)
								rpk_reader.seek(tm+144)
							model.skeleton=skeleton.name
							for m in range(bone_count):
								model.bone_name_list[skeleton.bone_list[m].skinID]=skeleton.bone_list[m].name
							
							rpk_file.skeleton_list.append(skeleton)
					if item2[0]==35:
						type3=rpk_reader.read_uint8(1)[0]
						list3=get_list(type3,rpk_reader)
						bone_count=None
						for item3 in list3:
							rpk_reader.seek(item3[1])
							if item3[0]==1:
								type4=rpk_reader.read_uint8(1)[0]
								list4=get_list(type4,rpk_reader)
								for item4 in list4:
									rpk_reader.seek(item4[1])
									flag=rpk_reader.read_uint8(4)
									if flag==(160,0,65,0):
										type5=rpk_reader.read_uint8(1)[0]
										list5=get_list(type5,rpk_reader)
										count=None
										for item5 in list5:
											rpk_reader.seek(item5[1])
											if item5[0]==22:
												count=rpk_reader.read_int32(1)[0]
											if item5[0]==23:
												stream_offset=rpk_reader.tell()
										if count is not None:
											rpk_reader.seek(stream_offset)
											model.bone_map_list.append(rpk_reader.read_int32(count))

			elif flag == (0,0,161,0):
				audio_count=audio_count+1
				type2=rpk_reader.read_uint8(1)[0]
				list2=get_list(type2,rpk_reader)
				
				audio=Audio()
				
				for item2 in list2:
					rpk_reader.seek(item2[1])
					
					if item2[0]==20:
						audio.chunk_name = rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==21:
						audio.name=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==100:
						audio.temp_path=rpk_reader.read_word(rpk_reader.read_int32(1)[0])
					if item2[0]==1:
						type3=rpk_reader.read_uint8(1)[0]
						list3=get_list(type3,rpk_reader)
						for item3 in list3:
							rpk_reader.seek(item3[1])
							if item3[0] == 30:
								rpk_reader.seek(item3[1])
								audio.size = rpk_reader.read_uint32(1)[0]
							if item3[0] == 31:
								audio.data = rpk_reader.read(audio.size)

				rpk_file.audio_list.append(audio)
			elif flag in [(27,6,65,0),(40,6,65,0),(42,6,65,0)]:#Final Gather Map ( Not implemented / not supported)
				final_gather_map_count=final_gather_map_count+1
				pass
			elif flag == (17, 1, 65, 0):#COL Data ( Not implemented / not supported)
				color_count=color_count+1
				pass
			elif flag == (0, 21, 65, 0):#INTERFACETEXTUREATLAS ( Not implemented / not supported)
				INTERFACETEXTUREATLAS_count=INTERFACETEXTUREATLAS_count+1
				pass
			elif flag == (39, 160, 0, 4):#Unknown Data, something with alphabetical letters
				alphabetical_data_count=alphabetical_data_count+1
				pass
			elif flag == (40, 160, 0, 4):#CliffData ( Not implemented / not supported)
				cliff_count=cliff_count+1
				pass
			elif flag in [(187,0,65,0),(2,0,65,0),(3,0,65,0)]:#Shader	(Not implemented / not supported)
				shader_count=shader_count+1
				pass
			else:
				print 'unknow global flag:',flag,rpk_reader.tell()
		
	print "Detected	:	"+add_leading_zeros(image_count)+"{0} images".format(image_count)
	print "Detected	:	"+add_leading_zeros(animation_count)+"{0} animations".format(animation_count)
	print "Detected	:	"+add_leading_zeros(mesh_count)+"{0} meshes".format(mesh_count)
	print "Detected	:	"+add_leading_zeros(material_count)+"{0} materials".format(material_count)
	print "Detected	:	"+add_leading_zeros(model_count)+"{0} models".format(model_count)
	print "Detected	:	"+add_leading_zeros(audio_count)+"{0} audios".format(audio_count)
	print "Detected	:	"+add_leading_zeros(final_gather_map_count)+"{0} final_gather_maps".format(final_gather_map_count)
	print "Detected	:	"+add_leading_zeros(color_count)+"{0} colors".format(color_count)
	print "Detected	:	"+add_leading_zeros(INTERFACETEXTUREATLAS_count)+"{0} INTERFACETEXTUREATLAS".format(INTERFACETEXTUREATLAS_count)
	print "Detected	:	"+add_leading_zeros(alphabetical_data_count)+"{0} alphabetical_data".format(alphabetical_data_count)
	print "Detected	:	"+add_leading_zeros(cliff_count)+"{0} cliffs".format(cliff_count)
	print "Detected	:	"+add_leading_zeros(shader_count)+"{0} shaders".format(shader_count)

	resource_file.close()

	return rpk_file

def save_data(data):
	########################################################################################################################################################################
	## Write necessary data to new files
	########################################################################################################################################################################

	print
	print "-"*50
	print "Write necessary data to new files"
	print "-"*50
	print

	if len(data.image_list)>0 or len(data.animation_list)>0 or len(data.audio_list)>0:
		print "Parent directory created" 
		create_new_directory(file_directory+os.sep+file_basename)
	print

	if len(data.image_list)>0:
		print "Image subdirectory created"
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'images')

	for image in data.image_list:
		print "	"+"*"*50
		print "	Writing	image to file"
		print "	Name	: {0}".format(image.name)
		print "	Height	: {0}".format(image.height)
		print "	Width	: {0}".format(image.width)
		print "	Format	: {0}".format(image.format)

		image_path=file_directory+os.sep+file_basename+os.sep+'images'+os.sep+image.name
		image_file=open(image_path,'wb')
		image_writer=BinaryWriter(image_file)

		if None not in (image.format, image.height, image.width, image.name,image.data):
			if 'DXT' in image.format:
				image_writer.write_to_dxt_file(image)
			elif 'tga' in image.format:
				if image.format=='tga32':
					offset='\x20\x20'
					data=image.data
				elif image.format=='tga16':
					offset='\x20\x20'
					data=tga_16(image.data)
				elif image.format=='tga24':
					offset='\x18\x20'
					data=image.data
				image_writer.write_to_tga_file(image,offset,data)
			elif image.format=='565to888':
				rgb565_to_rgb888(image.width,image.height,image.data,image.name)
			else:
				print 'Warning: unknown image format',image.format

		image_file.close()
		
	print "	"+"*"*50
	print

	if len(data.animation_list)>0:
		print "Animation subdirectory created"
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'animations')
	
	for action in data.animation_list:
		print "	"+"*"*50
		print "	Writing animation to file"
		print "	Name	: {0}".format(action.name)
		animation_path=file_directory+os.sep+file_basename+os.sep+'animations'+os.sep+action.name+'.anim'
		animation_file=open(animation_path,'wb')
		animation_writer=BinaryWriter(animation_file)
		
		for action_bone in action.bone_list:
			#print "		"+"+"*50
			#print "		Bone used by the animation"
			#print "		Name	: {0}".format(action_bone.name)
			animation_writer.write_word(action_bone.name)
			animation_writer.write_word('\x00')
			
			for i in action_bone.data:
				animation_writer.write_word(i)
		#print "		"+"+"*50
		animation_file.close()

	print "	"+"*"*50
	print

	if len(data.audio_list)>0:
		print "Audio subdirectory created"
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'audio')
	
	for audio in data.audio_list:
		print "	"+"*"*50
		print "	Writing audio to file"
		print "	Name	: {0}".format(audio.name)
		print "	Chunck	: {0}".format(audio.chunk_name)
		print "	Size	: {0}".format(audio.size)
		audio_path=file_directory+os.sep+file_basename+os.sep+'audio'+os.sep+audio.name+'.wav'
		audio_file=open(audio_path,'wb')
		audio_writer=BinaryWriter(audio_file)

		audio_writer.write_word(audio.data)

		audio_file.close()
	print "	"+"*"*50
	print

def create_blender_models(data):
########################################################################################################################################################################
## Create blender models
########################################################################################################################################################################

	print
	print "-"*50
	print "Try to create blender models and their dependencies"
	print "-"*50
	print

	for skeleton in data.skeleton_list:
		skeleton.draw()

	for model in data.model_list:
		print "	"+"*"*50
		print "	Name	: {0}".format(model.name)
		i=0
		for mesh_chunk,material_Chunk in model.mesh_list:
			print '			',mesh_chunk, ' -> ', material_Chunk
			mat=None
			for mat in data.material_list:
				if mat.chunk==material_Chunk:
					break
			for mesh in data.mesh_list:
				if mesh.chunk==mesh_chunk:
					print '			Mesh Name	:	',mesh.name
					MAT=Mat()
					if mesh.is_triangle==True:MAT.is_triangle=True
					if mesh.is_triangle_strip==True:MAT.is_triangle_strip=True
					if mat is not None:

						if mat.diffChunk is not None:
							if mat.diffChunk in data.texture_list.keys():
								mat.diffuse=file_directory+os.sep+file_basename+os.sep+'images'+os.sep+data.texture_list[mat.diffChunk]

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
	print "	"+"*"*50

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
					x,y,z=animation_reader.read_short(3,'h',14)
					x=degrees(x)
					y=degrees(y)
					z=degrees(z)
					bone.rotation_key_list.append(Euler(x,y,z).toMatrix().resize4x4())
			if type==30:
				for m in range(count):
					bone.rotation_frame_list.append(m)
					bone.rotation_key_list.append(quat_matrix(animation_reader.read_short(4,'h',15)).resize4x4())

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

	if file_extension=='prp' or file_extension=='pvp' or file_extension=='psp':
		extracted_data = read_data(full_file_path)
		save_data(extracted_data)
		create_blender_models(extracted_data)

	if file_extension=='anim':
		file=open(full_file_path,'rb')
		reader=BinaryReader(file)
		anim_file_parser(full_file_path,reader)
		file.close()

Blender.Window.FileSelector(openFile,'import','Overlord I and II files: prp - archive, pvp - archive, psp - archive, anim - animation')