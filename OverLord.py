import prpUnpackerLibraries
reload(prpUnpackerLibraries)
from prpUnpackerLibraries import *
import Blender
import math
from math import *

def safe(count):
	COUNT=0
	if count<100000:
		COUNT=count
	else:
		print 'warning:count:',count
	return COUNT

class Model:
	def __init__(self):
		self.name=None
		self.chunk=None
		self.mesh_list=[]
		self.bone_map_list=[]
		self.bone_name_list=[]
		self.skeleton=None

def get_item(list,ID):
	listA=[]
	for item in list:
		if item[0]==ID:
			listA.append(item)
	return listA

def get_list(type,g):
	list=[]
	if type>=128:
		count_small=type-128
		count_big=g.i(1)[0]
		for m in range(count_small):list.append(g.B(2))
		for m in range(count_big):list.append(g.i(2))
	else:
		count_small=type
		for m in range(count_small):list.append(g.B(2))
	position=g.tell()
	listA=[]
	for item in list:
		listA.append([item[0],position+item[1]])
	return listA

def prp_file_parser(filename,g):
	texture_list={}
	material_list=[]
	mesh_list=[]
	model_list=[]
	skeleton_list={}

	g.seek(16)
	g.word(160)

	type=g.B(1)[0]
	list=get_list(type,g)
	list26=get_item(list,26)
	for item in list26:
		#print item
		g.seek(item[1])
		g.B(3)
		type1=g.B(1)[0]
		list1=get_list(type1,g)
		for item1 in list1:
			g.seek(item1[1])
			flag=g.B(4)
			#print flag,g.tell(),

			if flag in [(61,0,65,0),(153,0,65,0),(152,0,65,0)]:#image
				#print 'image'
				type2=g.B(1)[0]
				list2=get_list(type2,g)
				for item2 in list2:
					g.seek(item2[1])
					if item2[0]==20:
						texture_chunk=g.word(g.i(1)[0])
						#print 'texture chunk:',texture_chunk
					if item2[0]==21:
						texture_name=g.word(g.i(1)[0])
					if item2[0]==1:
						type3=g.B(1)[0]
						list3=get_list(type3,g)
						for item3 in list3:
							g.seek(item3[1])
							#print item3
							if item3[0]==20:
								g.B(3)
								type4=g.B(1)[0]
								list4=get_list(type4,g)
								for item4 in list4:
									g.seek(item4[1])
									flag=g.B(4)
									if flag==(36,0,65,0):
										type5=g.B(1)[0]
										list5=get_list(type5,g)
										image=imageLib.Image()
										for item5 in list5:
											g.seek(item5[1])
											if item5[0]==20:
												image.szer=g.i(1)[0]
											if item5[0]==21:
												image.wys=g.i(1)[0]
											if item5[0]==23:
												format=g.i(1)[0]
											if item5[0]==22:
												offset=g.tell()
										g.seek(offset)
										if format==7:
											image.format='DXT1'
										elif format==11:
											image.format='DXT5'
										elif format==9:
											image.format='DXT3'
										elif format==5:
											image.format='tga32'
										else:
											print 'warning:format:',format,texture_name
										#print texture_name
										image.name=g.dirname+os.sep+g.basename.split('.')[0]+'_files'+os.sep+texture_name
										image.data=g.read(image.szer*image.wys*4)
										image.draw()
										texture_list[texture_chunk]=image.name
										break
									else:
										print 'unknow image flag:',flag,g.tell()

			elif flag==(5,0,65,0):#anim
				#print 'anim'

				animation_directory=g.dirname+os.sep+g.basename
				sys=Sys(animation_directory)
				sys.add_directory(sys.base+'_animfiles')

				type2=g.B(1)[0]
				list2=get_list(type2,g)

				list21=get_item(list2,21)
				for item21 in list21:
					g.seek(item21[1])
					animation_name=g.word(g.i(1)[0])

				animation_path=sys.dir+os.sep+sys.base+'_animfiles'+os.sep+animation_name+'.anim'
				animation_file=open(animation_path,'wb')
				p=BinaryReader(animation_file)

				list1=get_item(list2,1)
				for item1 in list1:
					g.seek(item1[1])
					type3=g.B(1)[0]
					list3=get_list(type3,g)
					list10=get_item(list3,10)
					for item10 in list10:
						g.seek(item10[1])
						g.B(3)
						type4=g.B(1)[0]
						list4=get_list(type4,g)
						for item4 in list4:
							g.seek(item4[1])
							flag=g.B(4)
							#print flag
							if flag==(7,0,65,0):#anim
								type5=g.B(1)[0]
								list5=get_list(type5,g)
								for item5 in list5:
									g.seek(item5[1])
									#print item5
									if item5[0]==20:
										boneName=g.word(g.i(1)[0])
										#print boneName
										animation_file.write(boneName)
										animation_file.write('\x00')
									if item5[0]==24:
										frame_count=None
										stream_offset=None
										type6=g.B(1)[0]
										list6=get_list(type6,g)
										for item6 in list6:
											g.seek(item6[1])
											#print '----',item6
											if item6[0]==21:
												frame_count=g.i(1)[0]
												#print '----position:',frame_count
											if item6[0]==22:
												stream_offset=g.tell()
										if (frame_count and stream_offset) is not None:
											g.seek(stream_offset)
											p.i([frame_count])
											for mC in range(frame_count):
												g.seek(2,1)
												animation_file.write(g.read(14))
										else:
											p.i([0])
										#print frame_count

									if item5[0]==25:

										frameCount30=None
										streamOffset31=None

										frameCount22=None
										streamOffset23=None
										type6=g.B(1)[0]
										list6=get_list(type6,g)
										for item6 in list6:
											g.seek(item6[1])
											#print '----',item6
											if item6[0]==21:
												type7=g.B(1)[0]
												list7=get_list(type7,g)
												for item7 in list7:
													g.seek(item7[1])
													#print '--------',item7
													if item7[0]==22:
														frameCount22=g.i(1)[0]
													if item7[0]==23:
														streamOffset23=g.tell()
													if item7[0]==30:
														frameCount30=g.i(1)[0]
													if item7[0]==31:
														streamOffset31=g.tell()
										#print frame_count
										if (frameCount22 and streamOffset23) is not None:
											g.seek(streamOffset23)
											p.i([frameCount22])
											p.B([22])
											for mC in range(frameCount22):
												animation_file.write(g.read(6))
												#print Euler(g.short(3,'h',15)).toQuat()

										elif (frameCount30 and streamOffset31) is not None:
											g.seek(streamOffset31)
											p.i([frameCount30])
											p.B([30])
											for mC in range(frameCount30):
												animation_file.write(g.read(8))
										else:
											p.i([0])
											p.B([0])

				animation_file.close()
				#break

				#break
			elif flag==(53,0,65,0):#mesh
				#print 'mesh'
				mesh=Mesh()
				mesh_list.append(mesh)
				type2=g.B(1)[0]
				list2=get_list(type2,g)
				for item2 in list2:
					g.seek(item2[1])
					if item2[0]==20:
						mesh.chunk=g.word(g.i(1)[0])
					if item2[0]==21:
						mesh.name=g.word(g.i(1)[0])
					if item2[0]==1:
						type3=g.B(1)[0]
						list3=get_list(type3,g)
						for item3 in list3:
							g.seek(item3[1])
							if item3[0]==10:
								type4=g.B(1)[0]
								list4=get_list(type4,g)
								indice_count=None
								for item4 in list4:
									g.seek(item4[1])
									if item4[0]==21:
										indice_count=g.i(1)[0]
										#print indice_count
									if item4[0]==22:
										indice_offset=g.tell()
								if indice_count is not None:
									mesh.indice_list=g.H(indice_count)
									mesh.is_triangle=True
									mesh.matrix=Euler(90,0,0).toMatrix().resize4x4()

							if item3[0]==21:
								type4=g.B(1)[0]
								list4=get_list(type4,g)
								indice_count=None
								for item4 in list4:
									g.seek(item4[1])
									if item4[0]==21:
										indice_count=g.i(1)[0]
										#print indice_count
									if item4[0]==22:
										indice_offset=g.tell()

								if indice_count is not None:
									mesh.indice_list=g.H(indice_count)
									mesh.is_triangle_strip=True

							if item3[0]==11:
								type4=g.B(1)[0]
								list4=get_list(type4,g)
								for item4 in list4:
									#print item4
									g.seek(item4[1])
									if item4[0]==20:
										type5=g.B(1)[0]
										list5=get_list(type5,g)
										for item5 in list5:
											#print item5
											g.seek(item5[1])
											if item5[0]==21:
												vertice_stride_size=g.i(1)[0]
												#print 'vertice_stride_size:',vertice_stride_size
											if item5[0]==22:
												vertice_item_count=g.i(1)[0]
												#print 'vertice_item_count:',vertice_item_count
											if item5[0]==23:
												vertice_item_offset=g.tell()
												#print 'vertice_item_offset:',vertice_item_offset
										g.seek(vertice_item_offset)
										vertice_position_offset=None
										vertice_uv_offset=None
										skin_indice_offset=None
										skin_weight_offset=None
										offset=0
										for k in range(vertice_item_count):
											a,b,c,d=g.B(4)
											#print k,a,b,c,d,vertice_stride_size
											if c==1:vertice_position_offset=offset
											if c==5 and a==0:
												vertice_uv_offset=offset
												#print k,a,b,c,d,vertice_stride_size
											if c==11:skin_indice_offset=offset
											if c==10:skin_weight_offset=offset
											if d==2:offset+=12
											if d==1:offset+=8
											if d==3:offset+=16
											if d==4:offset+=1
											if d==7:offset+=1
											if d==15:offset+=4
									if item4[0]==21:
										vertice_count=g.i(1)[0]
										#print 'vertice_count:',vertice_count
									if item4[0]==21:
										stream_offset=g.tell()
										#print 'stream_offset:',stream_offset
				g.seek(stream_offset)
				for k in range(vertice_count):
					tk=g.tell()
					if vertice_position_offset is not None:
						g.seek(tk+vertice_position_offset)
						mesh.vertice_position_list.append(g.f(3))
					#g.seek(tk+30)
					#print g.B(7),g.f(4)
					if vertice_uv_offset is not None:
						g.seek(tk+vertice_uv_offset)
						mesh.vertice_uv_list.append(g.f(2))
					if skin_indice_offset is not None:
						i1,i2,i3=g.B(3)
						mesh.skin_indice_list.append([i1,i2])
					if skin_weight_offset is not None:
						w1,w2=g.B(2)
						w3=255-(w1+w2)
						#print weightList
						mesh.skin_weight_list.append([w1,w2])
					g.seek(tk+vertice_stride_size)
				#if vertice_uv_offset is not None:
				#	mesh.name=str(vertice_stride_size)
				#	mesh.draw()

			elif flag in [(82,6,65,0),(60,6,65,0),(36,6,65,0),(10,6,65,0),(15,6,65,0),(8,6,65,0),(54,6,65,0),(38,6,65,0),(18,6,65,0),(22,6,65,0),(32,6,65,0)]:#material
				#print 'material'
				type2=g.B(1)[0]
				list2=get_list(type2,g)
				material=Mat()
				material.diffChunk=None
				material_list.append(material)
				for item2 in list2:
					g.seek(item2[1])
					if item2[0]==20:
						material.chunk=g.word(g.i(1)[0])
						#print 'material chunk:',material.chunk
					if item2[0]==21:
						material.name=g.word(g.i(1)[0])
					if item2[0]==30:
						type3=g.B(1)[0]
						list3=get_list(type3,g)
						for item3 in list3:
							g.seek(item3[1])
							#print item3
							if item3[0]==20:
								chunk=g.word(g.i(1)[0])
								#print 'diff chunk:',chunk
								material.diffChunk=chunk
								#if chunk in texture_list.keys():
								#	material.diffuse=texture_list[chunk]
								#	print material.diffuse
							if item3[0]==21:
								name=g.word(g.i(1)[0])
								#print name

			elif flag in [(75,0,65,0)]:#model
				#print 'model'
				model=Model()
				model_list.append(model)
				type2=g.B(1)[0]
				list2=get_list(type2,g)
				for item2 in list2:
					g.seek(item2[1])
					if item2[0]==20:
						model.chunk=g.word(g.i(1)[0])
					if item2[0]==21:
						model.name=g.word(g.i(1)[0])
					if item2[0]==30:
						type3=g.B(1)[0]
						list3=get_list(type3,g)
						for item3 in list3:
							g.seek(item3[1])
							#print item3
							if item3[0]==1:
								type4=g.B(1)[0]
								list4=get_list(type4,g)
								for item4 in list4:
									g.seek(item4[1])
									flag=g.B(4)
									if flag==(103,0,65,0):
										type5=g.B(1)[0]
										list5=get_list(type5,g)
										mesh_chunk,material_Chunk=None,None
										for item5 in list5:
											g.seek(item5[1])
											if item5[0]==31:
												type6=g.B(1)[0]
												list6=get_list(type6,g)
												for item6 in list6:
													g.seek(item6[1])
													if item6[0]==20:
														chunk=g.word(g.i(1)[0])
														#print chunk
														mesh_chunk=chunk
											if item5[0]==33:
												type6=g.B(1)[0]
												list6=get_list(type6,g)
												for item6 in list6:
													g.seek(item6[1])
													if item6[0]==20:
														chunk=g.word(g.i(1)[0])
														#print chunk
														material_Chunk=chunk
										if (mesh_chunk and material_Chunk) is not None:
											model.mesh_list.append([mesh_chunk,material_Chunk])
					if item2[0]==33:
						type3=g.B(1)[0]
						list3=get_list(type3,g)
						bone_count=None
						for item3 in list3:
							g.seek(item3[1])
							#print item3
							if item3[0]==20:
								g.i(1)[0]
							if item3[0]==21:
								bone_count=g.i(1)[0]
							if item3[0]==22:
								stream_offset=g.tell()
						if bone_count is not None:
							skeleton=Skeleton()
							skeleton.bone_space=True
							skeleton.NICE=True
							skeleton.name=model.name
							for m in range(safe(bone_count)):
								tm=g.tell()
								bone=Bone()
								bone.name=g.word(32)
								bone.matrix=matrix_4x4(g.f(16))
								g.f(4)
								g.f(3)
								a,b,c,d,e=g.i(5)
								bone.parent_id=b
								bone.skinID=a
								model.bone_name_list.append(bone.name)
								skeleton.bone_list.append(bone)
								g.seek(tm+144)
							skeleton.draw()
							model.skeleton=skeleton.name
							for m in range(bone_count):
								model.bone_name_list[skeleton.bone_list[m].skinID]=skeleton.bone_list[m].name
					if item2[0]==35:
						type3=g.B(1)[0]
						list3=get_list(type3,g)
						bone_count=None
						for item3 in list3:
							g.seek(item3[1])
							#print item3
							if item3[0]==1:
								type4=g.B(1)[0]
								list4=get_list(type4,g)
								for item4 in list4:
									g.seek(item4[1])
									flag=g.B(4)
									#print flag
									if flag==(160,0,65,0):
										type5=g.B(1)[0]
										list5=get_list(type5,g)
										count=None
										for item5 in list5:
											g.seek(item5[1])
											if item5[0]==22:
												count=g.i(1)[0]
												#print count
											if item5[0]==23:
												stream_offset=g.tell()
										if count is not None:
											g.seek(stream_offset)
											model.bone_map_list.append(g.i(count))

			elif flag == (0,0,161,0):
				pass#print 'audio clip'
			else:
				print 'unknow global flag:',flag,g.tell()

	for model in model_list:
		print 'model:',model.name
		i=0
		for mesh_chunk,material_Chunk in model.mesh_list:
			print ' '*4,mesh_chunk,material_Chunk
			mat=None
			for mat in material_list:
				if mat.chunk==material_Chunk:
					break
			for mesh in mesh_list:
				if mesh.chunk==mesh_chunk:
					
					MAT=Mat()
					if mesh.is_triangle==True:MAT.is_triangle=True
					if mesh.is_triangle_strip==True:MAT.is_triangle_strip=True
					if mat is not None:

						if mat.diffChunk is not None:
							if mat.diffChunk in texture_list.keys():
								mat.diffuse=texture_list[mat.diffChunk]

						MAT.diffuse=mat.diffuse
					mesh.material_list.append(MAT)
					mesh.bone_name_list=model.bone_name_list
					if i<len(model.bone_map_list):
						skin=Skin()
						skin.bone_map=model.bone_map_list[i]
						#print len(skin.bone_map)
						mesh.skin_list.append(skin)

					mesh.bind_skeleton=model.skeleton
					#print len(mesh.vertice_position_list),len(mesh.skin_indice_list),len(mesh.skin_weight_list),len(mesh.bone_name_list)
					#mesh.name=mesh.chunk
					#print mesh.name,mat.name
					try:mesh.draw()
					except:
						#print 'warning:mesh:',mesh.name
						pass
					break
			i+=1

def anim_file_parser(filename,g):
	selObjectList=Blender.Object.GetSelected()
	if len(selObjectList)>0:
		armature=selObjectList[0]
		action=Action()
		action.skeleton=armature.name
		action.bone_space=True
		#action.armature_space=True
		action.bone_sort=True
		action.UPDATE=False

		while(True):
			if g.tell()>=g.file_size():break
			bone=ActionBone()
			action.bone_list.append(bone)
			bone.name=g.find('\x00')
			#print bone.name
			count=g.i(1)[0]
			for m in range(count):
				frame=g.H(1)[0]
				bone.position_frame_list.append(frame)
				bone.position_key_list.append(vector_matrix(g.f(3)))
			count=g.i(1)[0]
			type=g.B(1)[0]
			if type==22:#not supported
				for m in range(count):
					bone.rotation_frame_list.append(m)
					x,y,z=g.short(3,'h',14)
					x=degrees(x)
					y=degrees(y)
					z=degrees(z)
					#print x,y,z
					bone.rotation_key_list.append(Euler(x,y,z).toMatrix().resize4x4())
			if type==30:
				for m in range(count):
					bone.rotation_frame_list.append(m)
					bone.rotation_key_list.append(quat_matrix(g.short(4,'h',15)).resize4x4())

		action.draw()
		action.set_context()

def openFile(flagList):
	global input,output
	input_file=Input(flagList)
	output_file=output(flagList)
	filename=input_file.filename
	print
	print '='*70
	print filename
	print '='*70
	print
	ext=filename.split('.')[-1].lower()

	if ext=='prp':
		file=open(filename,'rb')
		g=BinaryReader(file)
		prp_file_parser(filename,g)
		file.close()

	if ext=='anim':
		file=open(filename,'rb')
		g=BinaryReader(file)
		anim_file_parser(filename,g)
		file.close()

Blender.Window.FileSelector(openFile,'import','Overlord I and II files: prp - archive, anim - animation')