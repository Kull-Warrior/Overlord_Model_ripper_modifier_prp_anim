import bpy
import sys
import os
import copy

# Get the directory of the current script
current_dir = os.path.dirname(bpy.data.filepath)
subfolder_path = os.path.join(current_dir, "prpUnpackerLibraries")

# Append it to sys.path if it's not already there
if current_dir not in sys.path:
    sys.path.append(current_dir)

if subfolder_path not in sys.path:
    sys.path.append(subfolder_path)

import prpUnpackerLibraries
from prpUnpackerLibraries import *
import math
from math import *
import struct
import traceback
import mathutils
from mathutils import Euler, Matrix, Vector

# settings
ORIENT_BONES_TO_CHILDREN = True		# point bones at their children instead of keeping the game bone axes
IMPORT_CUSTOM_NORMALS = True		# use the normals stored in the file
SCENE_FPS = None					# None = frame rate of the file (15)
ANIMATION_MATCH_THRESHOLD = 0.5		# min. fraction of animated bones that must exist in a skeleton

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
	print ('Title		:	',rpk_file.name)
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
						texture_chunk=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
					if item2[0]==21:
						image.name=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
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

										if 'DXT' in image.format:
											mipmap_count=math.floor(math.log(max(image.width,image.height),2))+1

											if image.format=='DXT1':
												block_size=8
											else:
												block_size=16

											temp_width=image.width
											temp_height=image.height

											for x in range(mipmap_count):
												blocks_width = math.ceil(float(temp_width) / float(4))
												blocks_height = math.ceil(float(temp_height) / float(4))
												size = blocks_width * blocks_height * block_size
												image.data.extend(rpk_reader.read(size))

												if x < mipmap_count - 1:
													rpk_reader.read(25)

												temp_width=math.ceil(temp_width/2)
												temp_height=math.ceil(temp_height/2)
										else:
											size = image.width*image.height*4
											image.data=rpk_reader.read(size)

										rpk_file.image_list.append(image)
										rpk_file.texture_list[texture_chunk]=image.name
										break
									else:
										print ('unknow image flag:',flag,rpk_reader.tell())

			elif flag==(5,0,65,0):#anim
				animation_count=animation_count+1
				action=Action()

				type2=rpk_reader.read_uint8(1)[0]
				list2=get_list(type2,rpk_reader)

				for item2 in list2:
					rpk_reader.seek(item2[1])
					if item2[0]==21:
						action.name=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
					if item2[0]==30:
						action.fps=rpk_reader.read_float32(1)[0]
					if item2[0]==31:
						action.duration_us=rpk_reader.read_uint32(1)[0]

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
							if flag==(7,0,65,0):#bone track
								type5=rpk_reader.read_uint8(1)[0]
								list5=get_list(type5,rpk_reader)
								action_bone=ActionBone()
								for item5 in list5:
									rpk_reader.seek(item5[1])
									if item5[0]==20:
										action_bone.name=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
									if item5[0]==24:#position keys
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
										if position_frame_count is not None and position_stream_offset is not None and safe(position_frame_count):
											rpk_reader.seek(position_stream_offset)
											for mC in range(position_frame_count):
												time_us=rpk_reader.read_uint32(1)[0]
												position=rpk_reader.read_float32(3)
												action_bone.position_keys.append((time_us,position))

									if item5[0]==25:#rotation keys
										rotation_frame_count=None
										rotation_stream_offset=None
										sign_offset=None
										scale_frame_count=None
										scale_stream_offset=None
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
													if item7[0]==24:
														sign_offset=rpk_reader.tell()
													if item7[0]==30:
														scale_frame_count=rpk_reader.read_int32(1)[0]
													if item7[0]==31:
														scale_stream_offset=rpk_reader.tell()
										if rotation_frame_count is not None and rotation_stream_offset is not None and safe(rotation_frame_count):
											rpk_reader.seek(rotation_stream_offset)
											records=[rpk_reader.read(6) for mC in range(rotation_frame_count)]
											signs=b''
											if sign_offset is not None:
												rpk_reader.seek(sign_offset)
												signs=rpk_reader.read((rotation_frame_count+7)//8)
											action_bone.decode_rotation(records,signs)
										if scale_frame_count is not None and scale_stream_offset is not None:
											print ('Warning: scale keys are not supported (bone',action_bone.name,')')
								if action_bone.name is not None:
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
						mesh.chunk=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
					if item2[0]==21:
						mesh.name=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
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
										vertice_normal_offset=None
										vertice_uv_offset=None
										skin_indice_offsets=[]
										skin_weight_offsets=[]
										offset=0
										for k in range(vertice_item_count):
											a,b,c,d=rpk_reader.read_uint8(4)
											if c==1:vertice_position_offset=offset
											if c==4 and vertice_normal_offset is None:vertice_normal_offset=offset
											if c==5 and a==0:
												vertice_uv_offset=offset
											if c==11:skin_indice_offsets.append(offset)
											if c==10:skin_weight_offsets.append(offset)
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
						mesh.vertice_position_list.append(rpk_reader.read_float32(3))
					if vertice_normal_offset is not None:
						rpk_reader.seek(tk+vertice_normal_offset)
						mesh.vertice_normal_list.append(rpk_reader.read_float32(3))
					if vertice_uv_offset is not None:
						rpk_reader.seek(tk+vertice_uv_offset)
						mesh.vertice_uv_list.append(rpk_reader.read_float32(2))
					if skin_indice_offsets:
						indices=[]
						for so in skin_indice_offsets:
							rpk_reader.seek(tk+so)
							indices.append(rpk_reader.read_uint8(1)[0])
						mesh.skin_indice_list.append(indices)
					if skin_weight_offsets:
						weights=[]
						for so in skin_weight_offsets:
							rpk_reader.seek(tk+so)
							weights.append(rpk_reader.read_uint8(1)[0])
						#third weight is implicit
						if skin_indice_offsets and len(weights)<len(skin_indice_offsets):
							weights.append(max(0,255-sum(weights)))
						mesh.skin_weight_list.append(weights)
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
						material.chunk=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
					if item2[0]==21:
						material.name=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
					if item2[0]==30:
						type3=rpk_reader.read_uint8(1)[0]
						list3=get_list(type3,rpk_reader)
						for item3 in list3:
							rpk_reader.seek(item3[1])
							if item3[0]==20:
								chunk=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
								material.diffChunk=chunk
							if item3[0]==21:
								material.texture_file=rpk_reader.read_string(rpk_reader.read_int32(1)[0])

			elif flag in [(75,0,65,0)]:#model
				model_count=model_count+1
				model=Model()
				rpk_file.model_list.append(model)
				type2=rpk_reader.read_uint8(1)[0]
				list2=get_list(type2,rpk_reader)
				for item2 in list2:
					rpk_reader.seek(item2[1])
					if item2[0]==20:
						model.chunk=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
					if item2[0]==21:
						model.name=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
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
														chunk=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
														mesh_chunk=chunk
											if item5[0]==33:
												type6=rpk_reader.read_uint8(1)[0]
												list6=get_list(type6,rpk_reader)
												for item6 in list6:
													rpk_reader.seek(item6[1])
													if item6[0]==20:
														chunk=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
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
							skeleton.name=model.name
							skeleton.orient_bones_to_children=ORIENT_BONES_TO_CHILDREN
							model.bone_name_list={}
							for m in range(bone_count):
								tm=rpk_reader.tell()
								bone=Bone()
								bone.name=rpk_reader.read_string(32)
								bone.matrix=row_matrix_to_column(rpk_reader.read_float32(16))
								rpk_reader.read_float32(4)
								rpk_reader.read_float32(3)
								skin_id,parent_id,next_sibling,first_child,bone_flags=rpk_reader.read_int32(5)
								bone.parent_id=parent_id
								bone.skin_id=skin_id
								if skin_id>=0:
									model.bone_name_list[skin_id]=bone.name
								skeleton.bone_list.append(bone)
								rpk_reader.seek(tm+144)
							model.skeleton=skeleton
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
						audio.chunk_name = rpk_reader.read_string(rpk_reader.read_int32(1)[0])
					if item2[0]==21:
						audio.name=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
					if item2[0]==100:
						audio.temp_path=rpk_reader.read_string(rpk_reader.read_int32(1)[0])
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
				print ('unknow global flag:',flag,rpk_reader.tell())

	# Define the start and end byte sequences
	start_sequence = b'\x1B\x4C\x75\x61\x50'	# Hex values for "1B 4C 75 61 50"
	end_sequence = b'\x1B\x80\x00\x00'			# Hex values for "1B 80 00 00"

	# Extract the byte arrays between start and end sequences
	lua_data = rpk_reader.extract_byte_arrays(start_sequence, end_sequence)

	print(len(lua_data))

	for bytecode_data in lua_data:
		bytecode = LuaByteCode()
		bytecode.data = bytecode_data

		rpk_file.lua_bytecode_list.append(bytecode)

	print ("Detected	:	"+add_leading_zeros(image_count)+"{0} images".format(image_count))
	print ("Detected	:	"+add_leading_zeros(animation_count)+"{0} animations".format(animation_count))
	print ("Detected	:	"+add_leading_zeros(mesh_count)+"{0} meshes".format(mesh_count))
	print ("Detected	:	"+add_leading_zeros(material_count)+"{0} materials".format(material_count))
	print ("Detected	:	"+add_leading_zeros(model_count)+"{0} models".format(model_count))
	print ("Detected	:	"+add_leading_zeros(audio_count)+"{0} audios".format(audio_count))
	print ("Detected	:	"+add_leading_zeros(final_gather_map_count)+"{0} final_gather_maps".format(final_gather_map_count))
	print ("Detected	:	"+add_leading_zeros(color_count)+"{0} colors".format(color_count))
	print ("Detected	:	"+add_leading_zeros(INTERFACETEXTUREATLAS_count)+"{0} INTERFACETEXTUREATLAS".format(INTERFACETEXTUREATLAS_count))
	print ("Detected	:	"+add_leading_zeros(alphabetical_data_count)+"{0} alphabetical_data".format(alphabetical_data_count))
	print ("Detected	:	"+add_leading_zeros(cliff_count)+"{0} cliffs".format(cliff_count))
	print ("Detected	:	"+add_leading_zeros(shader_count)+"{0} shaders".format(shader_count))
	print ("Detected	:	"+add_leading_zeros(len(rpk_file.lua_bytecode_list))+"{0} lua byte code".format(len(rpk_file.lua_bytecode_list)))

	resource_file.close()

	return rpk_file

def save_data(data, file_directory, file_basename):
	########################################################################################################################################################################
	## Write necessary data to new files
	########################################################################################################################################################################

	print ()
	print ("-"*50)
	print ("Write necessary data to new files")
	print ("-"*50)
	print ()

	if len(data.image_list)>0 or len(data.animation_list)>0 or len(data.audio_list)>0 or len(data.lua_bytecode_list)>0:
		print ("Parent directory created")
		create_new_directory(file_directory+os.sep+file_basename)
	print

	if len(data.image_list)>0:
		print ("Image subdirectory created")
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'images')

	for image in data.image_list:
		print ("	"+"*"*50)
		print ("	Writing	image to file")
		print ("	Name	: {0}".format(image.name))
		print ("	Height	: {0}".format(image.height))
		print ("	Width	: {0}".format(image.width))
		print ("	Format	: {0}".format(image.format))

		image_path=file_directory+os.sep+file_basename+os.sep+'images'+os.sep+image.name
		image_file=open(image_path,'wb')
		image_writer=BinaryWriter(image_file)

		if None not in (image.format, image.height, image.width, image.name,image.data):
			if 'DXT' in image.format:
				image_writer.write_to_dxt_file(image)
			elif 'tga' in image.format:
				if image.format=='tga32':
					offset=b'\x20\x20'
					temp_data=image.data
				elif image.format=='tga16':
					offset=b'\x20\x20'
					temp_data=tga_16(image.data)
				elif image.format=='tga24':
					offset=b'\x18\x20'
					temp_data=image.data
				image_writer.write_to_tga_file(image,offset,temp_data)
			else:
				print ('Warning: unknown image format',image.format)

		image_file.close()

	print ("	"+"*"*50)
	print ()

	if len(data.animation_list)>0:
		print ("Animation subdirectory created")
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'animations')

	for action in data.animation_list:
		print ("	"+"*"*50)
		print ("	Writing animation to file")
		print ("	Name	: {0}".format(action.name))
		animation_path=file_directory+os.sep+file_basename+os.sep+'animations'+os.sep+action.name+'.anim'
		animation_file=open(animation_path,'wb')
		animation_writer=BinaryWriter(animation_file)
		write_anim_file(action,animation_writer)
		animation_file.close()

	print ("	"+"*"*50)
	print ()

	if len(data.audio_list)>0:
		print ("Audio subdirectory created")
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'audio')

	for audio in data.audio_list:
		print ("	"+"*"*50)
		print ("	Writing audio to file")
		print ("	Name	: {0}".format(audio.name))
		print ("	Chunck	: {0}".format(audio.chunk_name))
		print ("	Size	: {0}".format(audio.size))
		audio_path=file_directory+os.sep+file_basename+os.sep+'audio'+os.sep+audio.name+'.wav'
		audio_file=open(audio_path,'wb')
		audio_writer=BinaryWriter(audio_file)

		audio_writer.write_string(audio.data)

		audio_file.close()
	print ("	"+"*"*50)
	print ()

	if len(data.lua_bytecode_list)>0:
		print ("Lua bytecode subdirectory created")
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'lua_bytecode')

	count = 0
	for bytecode in data.lua_bytecode_list:
		bytecode.name = file_basename + "_lua_" + str(count)
		print ("	"+"*"*50)
		print ("	Writing lua bytecode to file")
		print ("	Size	: {0}".format(len(bytecode.data)))
		bytecode_path=file_directory+os.sep+file_basename+os.sep+'lua_bytecode'+os.sep+bytecode.name+'.luac'
		bytecode_file=open(bytecode_path,'wb')
		bytecode_writer=BinaryWriter(bytecode_file)
		bytecode_writer.write_string(bytecode.data)

		bytecode_file.close()
		count = count + 1

	print ("	"+"*"*50)
	print ()

def create_blender_models(data, file_directory, file_basename):
########################################################################################################################################################################
## Create blender models
########################################################################################################################################################################

	print ()
	print ("-"*50)
	print ("Try to create blender models and their dependencies")
	print ("-"*50)
	print ()

	if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
		bpy.ops.object.mode_set(mode='OBJECT')

	if SCENE_FPS is not None:
		bpy.context.scene.render.fps=int(SCENE_FPS)
		bpy.context.scene.render.fps_base=1.0
	elif len(data.animation_list)>0:
		bpy.context.scene.render.fps=int(round(data.animation_list[0].fps))
		bpy.context.scene.render.fps_base=1.0

	for model in data.model_list:
		print ("	"+"*"*50)
		print ("	Name	: {0}".format(model.name))

		collection=bpy.data.collections.new(model.name)
		bpy.context.scene.collection.children.link(collection)

		armature_name=None
		if model.skeleton is not None:
			model.skeleton.collection=collection
			model.skeleton.draw()
			armature_name=model.skeleton.object.name

		i=0
		for mesh_chunk,material_Chunk in model.mesh_list:
			print ('			',mesh_chunk, ' -> ', material_Chunk)
			mat=None
			for candidate in data.material_list:
				if candidate.chunk==material_Chunk:
					mat=candidate
					break
			for source in data.mesh_list:
				if source.chunk==mesh_chunk:
					print ('			Mesh Name	:	',source.name)
					mesh=copy.copy(source)
					mesh.material_list=[]
					mesh.material_id_list=[]
					mesh.triangle_list=[]
					mesh.skin_list=[]
					mesh.skin_id_list=[]
					mesh.object=None
					mesh.collection=collection
					mesh.use_custom_normals=IMPORT_CUSTOM_NORMALS
					MAT=Mat()
					if mesh.is_triangle==True:MAT.is_triangle=True
					if mesh.is_triangle_strip==True:MAT.is_triangle_strip=True
					if mat is not None:
						if mat.diffChunk is not None:
							if mat.diffChunk in data.texture_list.keys():
								mat.diffuse=file_directory+os.sep+file_basename+os.sep+'images'+os.sep+data.texture_list[mat.diffChunk]
						MAT.diffuse=mat.diffuse

					print ('			Material Name	:	',MAT.name)
					mesh.material_list.append(MAT)
					mesh.bone_name_list=model.bone_name_list
					if model.skeleton is not None:
						mesh.matrix=SKIN_TO_BLENDER
						if i<len(model.bone_map_list):
							skin=Skin()
							skin.bone_map=model.bone_map_list[i]
							mesh.skin_list.append(skin)
						mesh.bind_skeleton=armature_name
					else:
						mesh.matrix=GAME_TO_BLENDER
						mesh.bind_skeleton=None
					try:
						mesh.draw()
					except Exception:
						print ('			ERROR while creating mesh',source.name)
						traceback.print_exc()
					break
			i+=1

	create_blender_animations(data)

	bpy.context.scene.frame_current=bpy.context.scene.frame_start
	print ("	"+"*"*50)

def create_blender_animations(data):
	if len(data.animation_list)==0 or len(data.skeleton_list)==0:
		return
	print ()
	print ("-"*50)
	print ("Create animations")
	print ("-"*50)

	layouts={}
	for skeleton in data.skeleton_list:
		if skeleton.object is None:
			continue
		layouts.setdefault(skeleton.signature(),[]).append(skeleton)

	for action in data.animation_list:
		created=[]
		for signature,skeletons in layouts.items():
			score=action.matches(skeletons[0].bone_names())
			if score<ANIMATION_MATCH_THRESHOLD:
				continue
			created.append((score,skeletons))
		if not created:
			print ("	{0:<40s} : no matching skeleton".format(action.name))
			continue
		created.sort(key=lambda item:-item[0])
		for score,skeletons in created:
			action_name=action.name
			if len(created)>1:
				action_name="{0} [{1}]".format(action.name,skeletons[0].name)
			first=skeletons[0].object
			make_active=first.animation_data is None or first.animation_data.action is None
			blender_action=action.draw(first,action_name=action_name,set_active=make_active)
			for skeleton in skeletons[1:]:
				armature=skeleton.object
				if armature.animation_data is None or armature.animation_data.action is None:
					assign_action(armature,blender_action)
			print ("	{0:<40s} -> {1:<40s} ({2} bones, {3:.0f}% match, {4} frames)".format(action.name,action_name,len(action.bone_list),score*100,action.frame_count()))
	print ()

def anim_file_parser(filename,animation_reader):
	armature=bpy.context.active_object
	if armature is None or armature.type!='ARMATURE':
		for obj in bpy.context.selected_objects:
			if obj.type=='ARMATURE':
				armature=obj
				break
	if armature is None or armature.type!='ARMATURE':
		print ('Warning: select the armature that should receive the animation first')
		return
	name=os.path.basename(filename).rsplit('.',1)[0]
	action=read_anim_file(animation_reader,name)
	score=action.matches([bone.name for bone in armature.data.bones])
	print ('Animation',action.name,':',len(action.bone_list),'bones,','{0:.0f}% of them exist in'.format(score*100),armature.name)
	action.draw(armature,action_name=action.name,set_active=True)

def read_map_data(filename):
	resource_file=open(filename,'rb')
	omp_reader=BinaryReader(resource_file)

	overlord_map = OverlordMap()

	offset = omp_reader.get_map_data_offset(512,512)
	print("Map offset : ")
	print(offset)

	data = omp_reader.read_map_data_from_file(offset, 512, 512)

	# Define the start and end byte sequences
	start_sequence = b'\x1B\x4C\x75\x61\x50'	# Hex values for "1B 4C 75 61 50"
	end_sequence = b'\x1B\x80\x00\x00'			# Hex values for "1B 80 00 00"

	# Extract the byte arrays between start and end sequences
	lua_data = omp_reader.extract_byte_arrays(start_sequence, end_sequence)

	for bytecode_data in lua_data:
		bytecode = LuaByteCode()
		bytecode.data = bytecode_data

		overlord_map.lua_bytecode_list.append(bytecode)

	overlord_map.set_map_data(data)
	overlord_map.water_level = omp_reader.get_map_water_level(filename)

	resources_list = omp_reader.get_resource_files(filename)

	overlord_map.rpk_resources = omp_reader.get_rpk_resources()

	#environment = omp_reader.get_environment()

	environments = []
	for rpk_file in overlord_map.rpk_resources:
		# Extract environment string
		if 'Exp - Env ' in rpk_file:
			start = rpk_file.find('Exp - Env ')
			env_str = rpk_file[start:]
		elif 'Env ' in rpk_file:
			# Find all Env occurrences
			matches = list(re.finditer('Env ', rpk_file))
			if len(matches) > 1:
				start = matches[-1].start()
			else:
				start = rpk_file.find('Env ')
			env_str = rpk_file[start:]
		elif 'Environment ' in rpk_file:
			start = rpk_file.find('Environment ')
			env_str = rpk_file[start:]
		else:
			continue  # No valid environment found

		environments.append(env_str.strip())

	# Remove unwanted environments
	remove_list = [
		"Env Tower - Main",
		"Env Spawning Pits",
		"Env Spawning Pits",  # Intentional duplicate
		"Exp - MP Env Rocky Race",
		"Exp - Env HellSet",
		"Env Multiplayer 1",
		"Exp - MP Env Halls"
	]

	for env in remove_list:
		while env in environments:
			environments.remove(env)

	# Determine return value
	if "Exp - Warrior Abyss - 01" in filename and len(environments) >= 2:
		environment = environments[1]
	else:
		if environments:
			environment = environments[0]
		else:
			environment = "default"

	rpk_environment_file_path = None

	if len(resources_list) > 0:
		for resource_path in resources_list:
			if environment in resource_path:
				rpk_environment_file_path = resource_path

		if rpk_environment_file_path != None:
			file_directory=os.path.dirname(rpk_environment_file_path)
			file_extension=os.path.basename(rpk_environment_file_path).split('.')[-1]
			file_basename=os.path.basename(rpk_environment_file_path).split('.'+file_extension)[0]

			extracted_data = read_data(rpk_environment_file_path)
			save_data(extracted_data, file_directory, file_basename)

			for image in extracted_data.image_list:
				is_nm_texture = 'nm' in image.name.lower()
				if not is_nm_texture and image.height == 2048 and image.width == 2048:
					dds_path = file_directory+os.sep+file_basename+os.sep+'images'+os.sep+image.name

			try:
				# Load the DDS image using Blender's native support (DXT1/3/5)
				img = bpy.data.images.load(dds_path)
			except Exception as e:
				print(f"Failed to load {dds_path}: {e}")

			# Get image dimensions and pixel data (pixels are in RGBA order)
			width, height = img.size
			pixels = list(img.pixels)

			# Composite over a white background (adjust the background color if needed)
			# For each pixel: new_color = alpha * original + (1 - alpha) * background
			for i in range(0, len(pixels), 4):
				r, g, b, a = pixels[i:i+4]
				# White background means background color = (1, 1, 1)
				pixels[i]   = r
				pixels[i+1] = g
				pixels[i+2] = b
				# Set alpha to 1 (opaque)
				pixels[i+3] = 1.0

			# Create a new image to store the composited result
			new_img = bpy.data.images.new(name=img.name.replace(".dds",".png"), width=width, height=height)
			new_img.pixels = pixels
			new_img.file_format = 'PNG'

			overlord_map.texture_atlas = new_img

	if overlord_map.texture_atlas == None:
		# Get the directory of the current script
		current_dir = os.path.dirname(bpy.data.filepath)
		resources_path = os.path.join(current_dir, "resources\\Env Halfling.png")
		overlord_map.texture_atlas = bpy.data.images.load(resources_path)

	print ("Detected	:	"+add_leading_zeros(len(overlord_map.lua_bytecode_list))+"{0} lua byte code".format(len(overlord_map.lua_bytecode_list)))
	print ("Detected	:	"+add_leading_zeros(len(overlord_map.rpk_resources))+"{0} rpk files".format(len(overlord_map.rpk_resources)))

	return overlord_map

def save_map_data(data, file_directory, file_basename):
	print ()
	print ("-"*50)
	print ("Write necessary data to new files")
	print ("-"*50)
	print ()

	if len(data.lua_bytecode_list)>0:
		print ("Parent directory created")
		create_new_directory(file_directory+os.sep+file_basename)
	print

	if len(data.lua_bytecode_list)>0:
		print ("Lua bytecode subdirectory created")
		create_new_directory(file_directory+os.sep+file_basename+os.sep+'lua_bytecode')

	count = 0
	for bytecode in data.lua_bytecode_list:
		bytecode.name = file_basename + "_lua_" + str(count)
		print ("	"+"*"*50)
		print ("	Writing lua bytecode to file")
		print ("	Size	: {0}".format(len(bytecode.data)))
		bytecode_path=file_directory+os.sep+file_basename+os.sep+'lua_bytecode'+os.sep+bytecode.name+'.luac'
		bytecode_file=open(bytecode_path,'wb')
		bytecode_writer=BinaryWriter(bytecode_file)
		bytecode_writer.write_string(bytecode.data)

		bytecode_file.close()
		count = count + 1

	print ("	"+"*"*50)
	print ()
def create_blender_terrain(data):
	data.create_full_terrain_scene()
	data.create_water_plane()

def openFile(full_file_path):
	file_directory=os.path.dirname(full_file_path)
	file_extension=os.path.basename(full_file_path).split('.')[-1]
	file_basename=os.path.basename(full_file_path).split('.'+file_extension)[0]

	print ()
	print ('='*70)
	print (full_file_path)
	print ('='*70)
	print ()

	if file_extension=='prp' or file_extension=='pvp' or file_extension=='psp':
		extracted_data = read_data(full_file_path)
		save_data(extracted_data, file_directory, file_basename)
		create_blender_models(extracted_data, file_directory, file_basename)

	if file_extension=='anim':
		file=open(full_file_path,'rb')
		reader=BinaryReader(file)
		anim_file_parser(full_file_path,reader)
		file.close()

	if file_extension=='omp':
		extracted_data = read_map_data(full_file_path)
		save_map_data(extracted_data, file_directory, file_basename)
		create_blender_terrain(extracted_data)

if __name__ == "__main__":
	openFile("C:\\Program Files (x86)\\Steam\\steamapps\\common\\Overlord\\Resources\\Character Minion Master.prp")