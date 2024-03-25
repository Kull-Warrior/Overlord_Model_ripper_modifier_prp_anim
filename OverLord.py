import newGameLib
reload(newGameLib)
from newGameLib import *
import Blender
import math
from math import *

def safe(count):
	COUNT=0
	if count<100000:
		COUNT=count
	else:
		print 'WARNING:count:',count
	return COUNT

class Model:
	def __init__(self):
		self.name=None
		self.chunk=None
		self.meshList=[]
		self.boneMapList=[]
		self.boneNameList=[]
		self.skeleton=None

def getItem(list,ID):
	listA=[]
	for item in list:
		if item[0]==ID:
			listA.append(item)
	return listA

def getList(type,g):
	list=[]
	if type>=128:
		countsmall=type-128
		countbig=g.i(1)[0]
		for m in range(countsmall):list.append(g.B(2))
		for m in range(countbig):list.append(g.i(2))
	else:
		countsmall=type
		for m in range(countsmall):list.append(g.B(2))
	pos=g.tell()
	listA=[]
	for item in list:
		listA.append([item[0],pos+item[1]])
	return listA

def prpParser(filename,g):
	texList={}
	matList=[]
	meshList=[]
	modelList=[]
	skeletonList={}

	g.seek(16)
	g.word(160)

	type=g.B(1)[0]
	list=getList(type,g)
	list26=getItem(list,26)
	for item in list26:
		#print item
		g.seek(item[1])
		g.B(3)
		type1=g.B(1)[0]
		list1=getList(type1,g)
		for item1 in list1:
			g.seek(item1[1])
			flag=g.B(4)
			#print flag,g.tell(),

			if flag in [(61,0,65,0),(153,0,65,0),(152,0,65,0)]:#image
				#print 'image'
				type2=g.B(1)[0]
				list2=getList(type2,g)
				for item2 in list2:
					g.seek(item2[1])
					if item2[0]==20:
						texChunk=g.word(g.i(1)[0])
						#print 'tex chunk:',texChunk
					if item2[0]==21:
						texName=g.word(g.i(1)[0])
					if item2[0]==1:
						type3=g.B(1)[0]
						list3=getList(type3,g)
						for item3 in list3:
							g.seek(item3[1])
							#print item3
							if item3[0]==20:
								g.B(3)
								type4=g.B(1)[0]
								list4=getList(type4,g)
								for item4 in list4:
									g.seek(item4[1])
									flag=g.B(4)
									if flag==(36,0,65,0):
										type5=g.B(1)[0]
										list5=getList(type5,g)
										img=imageLib.Image()
										for item5 in list5:
											g.seek(item5[1])
											if item5[0]==20:
												img.szer=g.i(1)[0]
											if item5[0]==21:
												img.wys=g.i(1)[0]
											if item5[0]==23:
												format=g.i(1)[0]
											if item5[0]==22:
												offset=g.tell()
										g.seek(offset)
										if format==7:
											img.format='DXT1'
										elif format==11:
											img.format='DXT5'
										elif format==9:
											img.format='DXT3'
										elif format==5:
											img.format='tga32'
										else:
											print 'WARNING:format:',format,texName
										#print texName
										img.name=g.dirname+os.sep+g.basename.split('.')[0]+'_files'+os.sep+texName
										img.data=g.read(img.szer*img.wys*4)
										img.draw()
										texList[texChunk]=img.name
										break
									else:
										print 'unknow image flag:',flag,g.tell()

			elif flag==(5,0,65,0):#anim
				#print 'anim'

				animDir=g.dirname+os.sep+g.basename
				sys=Sys(animDir)
				sys.addDir(sys.base+'_animfiles')

				type2=g.B(1)[0]
				list2=getList(type2,g)

				list21=getItem(list2,21)
				for item21 in list21:
					g.seek(item21[1])
					animName=g.word(g.i(1)[0])

				animPath=sys.dir+os.sep+sys.base+'_animfiles'+os.sep+animName+'.anim'
				animFile=open(animPath,'wb')
				p=BinaryReader(animFile)

				list1=getItem(list2,1)
				for item1 in list1:
					g.seek(item1[1])
					type3=g.B(1)[0]
					list3=getList(type3,g)
					list10=getItem(list3,10)
					for item10 in list10:
						g.seek(item10[1])
						g.B(3)
						type4=g.B(1)[0]
						list4=getList(type4,g)
						for item4 in list4:
							g.seek(item4[1])
							flag=g.B(4)
							#print flag
							if flag==(7,0,65,0):#anim
								type5=g.B(1)[0]
								list5=getList(type5,g)
								for item5 in list5:
									g.seek(item5[1])
									#print item5
									if item5[0]==20:
										boneName=g.word(g.i(1)[0])
										#print boneName
										animFile.write(boneName)
										animFile.write('\x00')
									if item5[0]==24:
										frameCount=None
										streamOffset=None
										type6=g.B(1)[0]
										list6=getList(type6,g)
										for item6 in list6:
											g.seek(item6[1])
											#print '----',item6
											if item6[0]==21:
												frameCount=g.i(1)[0]
												#print '----pos:',frameCount
											if item6[0]==22:
												streamOffset=g.tell()
										if (frameCount and streamOffset) is not None:
											g.seek(streamOffset)
											p.i([frameCount])
											for mC in range(frameCount):
												g.seek(2,1)
												animFile.write(g.read(14))
										else:
											p.i([0])
										#print frameCount

									if item5[0]==25:

										frameCount30=None
										streamOffset31=None

										frameCount22=None
										streamOffset23=None
										type6=g.B(1)[0]
										list6=getList(type6,g)
										for item6 in list6:
											g.seek(item6[1])
											#print '----',item6
											if item6[0]==21:
												type7=g.B(1)[0]
												list7=getList(type7,g)
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
										#print frameCount
										if (frameCount22 and streamOffset23) is not None:
											g.seek(streamOffset23)
											p.i([frameCount22])
											p.B([22])
											for mC in range(frameCount22):
												animFile.write(g.read(6))
												#print Euler(g.short(3,'h',15)).toQuat()

										elif (frameCount30 and streamOffset31) is not None:
											g.seek(streamOffset31)
											p.i([frameCount30])
											p.B([30])
											for mC in range(frameCount30):
												animFile.write(g.read(8))
										else:
											p.i([0])
											p.B([0])

				animFile.close()
				#break

				#break
			elif flag==(53,0,65,0):#mesh
				#print 'mesh'
				mesh=Mesh()
				meshList.append(mesh)
				type2=g.B(1)[0]
				list2=getList(type2,g)
				for item2 in list2:
					g.seek(item2[1])
					if item2[0]==20:
						mesh.chunk=g.word(g.i(1)[0])
					if item2[0]==21:
						mesh.name=g.word(g.i(1)[0])
					if item2[0]==1:
						type3=g.B(1)[0]
						list3=getList(type3,g)
						for item3 in list3:
							g.seek(item3[1])
							if item3[0]==10:
								type4=g.B(1)[0]
								list4=getList(type4,g)
								indiceCount=None
								for item4 in list4:
									g.seek(item4[1])
									if item4[0]==21:
										indiceCount=g.i(1)[0]
										#print indiceCount
									if item4[0]==22:
										indiceOffset=g.tell()
								if indiceCount is not None:
									mesh.indiceList=g.H(indiceCount)
									mesh.TRIANGLE=True
									mesh.matrix=Euler(90,0,0).toMatrix().resize4x4()

							if item3[0]==21:
								type4=g.B(1)[0]
								list4=getList(type4,g)
								indiceCount=None
								for item4 in list4:
									g.seek(item4[1])
									if item4[0]==21:
										indiceCount=g.i(1)[0]
										#print indiceCount
									if item4[0]==22:
										indiceOffset=g.tell()

								if indiceCount is not None:
									mesh.indiceList=g.H(indiceCount)
									mesh.TRISTRIP=True

							if item3[0]==11:
								type4=g.B(1)[0]
								list4=getList(type4,g)
								for item4 in list4:
									#print item4
									g.seek(item4[1])
									if item4[0]==20:
										type5=g.B(1)[0]
										list5=getList(type5,g)
										for item5 in list5:
											#print item5
											g.seek(item5[1])
											if item5[0]==21:
												vertStrideSize=g.i(1)[0]
												#print 'vertStrideSize:',vertStrideSize
											if item5[0]==22:
												vertItemCount=g.i(1)[0]
												#print 'vertItemCount:',vertItemCount
											if item5[0]==23:
												vertItemOffset=g.tell()
												#print 'vertItemOffset:',vertItemOffset
										g.seek(vertItemOffset)
										verPosOff=None
										vertUVOff=None
										skinIndiceOff=None
										skinWeightOff=None
										off=0
										for k in range(vertItemCount):
											a,b,c,d=g.B(4)
											#print k,a,b,c,d,vertStrideSize
											if c==1:vertPosOff=off
											if c==5 and a==0:
												vertUVOff=off
												#print k,a,b,c,d,vertStrideSize
											if c==11:skinIndiceOff=off
											if c==10:skinWeightOff=off
											if d==2:off+=12
											if d==1:off+=8
											if d==3:off+=16
											if d==4:off+=1
											if d==7:off+=1
											if d==15:off+=4
									if item4[0]==21:
										vertCount=g.i(1)[0]
										#print 'vertCount:',vertCount
									if item4[0]==21:
										streamOffset=g.tell()
										#print 'streamOffset:',streamOffset
				g.seek(streamOffset)
				for k in range(vertCount):
					tk=g.tell()
					if vertPosOff is not None:
						g.seek(tk+vertPosOff)
						mesh.vertPosList.append(g.f(3))
					#g.seek(tk+30)
					#print g.B(7),g.f(4)
					if vertUVOff is not None:
						g.seek(tk+vertUVOff)
						mesh.vertUVList.append(g.f(2))
					if skinIndiceOff is not None:
						i1,i2,i3=g.B(3)
						mesh.skinIndiceList.append([i1,i2])
					if skinWeightOff is not None:
						w1,w2=g.B(2)
						w3=255-(w1+w2)
						#print weightList
						mesh.skinWeightList.append([w1,w2])
					g.seek(tk+vertStrideSize)
				#if vertUVOff is not None:
				#	mesh.name=str(vertStrideSize)
				#	mesh.draw()

			elif flag in [(82,6,65,0),(60,6,65,0),(36,6,65,0),(10,6,65,0),(15,6,65,0),(8,6,65,0),(54,6,65,0),(38,6,65,0),(18,6,65,0),(22,6,65,0),(32,6,65,0)]:#material
				#print 'material'
				type2=g.B(1)[0]
				list2=getList(type2,g)
				mat=Mat()
				mat.diffChunk=None
				matList.append(mat)
				for item2 in list2:
					g.seek(item2[1])
					if item2[0]==20:
						mat.chunk=g.word(g.i(1)[0])
						#print 'mat chunk:',mat.chunk
					if item2[0]==21:
						mat.name=g.word(g.i(1)[0])
					if item2[0]==30:
						type3=g.B(1)[0]
						list3=getList(type3,g)
						for item3 in list3:
							g.seek(item3[1])
							#print item3
							if item3[0]==20:
								chunk=g.word(g.i(1)[0])
								#print 'diff chunk:',chunk
								mat.diffChunk=chunk
								#if chunk in texList.keys():
								#	mat.diffuse=texList[chunk]
								#	print mat.diffuse
							if item3[0]==21:
								name=g.word(g.i(1)[0])
								#print name

			elif flag in [(75,0,65,0)]:#model
				#print 'model'
				model=Model()
				modelList.append(model)
				type2=g.B(1)[0]
				list2=getList(type2,g)
				for item2 in list2:
					g.seek(item2[1])
					if item2[0]==20:
						model.chunk=g.word(g.i(1)[0])
					if item2[0]==21:
						model.name=g.word(g.i(1)[0])
					if item2[0]==30:
						type3=g.B(1)[0]
						list3=getList(type3,g)
						for item3 in list3:
							g.seek(item3[1])
							#print item3
							if item3[0]==1:
								type4=g.B(1)[0]
								list4=getList(type4,g)
								for item4 in list4:
									g.seek(item4[1])
									flag=g.B(4)
									if flag==(103,0,65,0):
										type5=g.B(1)[0]
										list5=getList(type5,g)
										meshChunk,matChunk=None,None
										for item5 in list5:
											g.seek(item5[1])
											if item5[0]==31:
												type6=g.B(1)[0]
												list6=getList(type6,g)
												for item6 in list6:
													g.seek(item6[1])
													if item6[0]==20:
														chunk=g.word(g.i(1)[0])
														#print chunk
														meshChunk=chunk
											if item5[0]==33:
												type6=g.B(1)[0]
												list6=getList(type6,g)
												for item6 in list6:
													g.seek(item6[1])
													if item6[0]==20:
														chunk=g.word(g.i(1)[0])
														#print chunk
														matChunk=chunk
										if (meshChunk and matChunk) is not None:
											model.meshList.append([meshChunk,matChunk])
					if item2[0]==33:
						type3=g.B(1)[0]
						list3=getList(type3,g)
						boneCount=None
						for item3 in list3:
							g.seek(item3[1])
							#print item3
							if item3[0]==20:
								g.i(1)[0]
							if item3[0]==21:
								boneCount=g.i(1)[0]
							if item3[0]==22:
								streamOffset=g.tell()
						if boneCount is not None:
							skeleton=Skeleton()
							skeleton.BONESPACE=True
							skeleton.NICE=True
							skeleton.name=model.name
							for m in range(safe(boneCount)):
								tm=g.tell()
								bone=Bone()
								bone.name=g.word(32)
								bone.matrix=Matrix4x4(g.f(16))
								g.f(4)
								g.f(3)
								a,b,c,d,e=g.i(5)
								bone.parentID=b
								bone.skinID=a
								model.boneNameList.append(bone.name)
								skeleton.boneList.append(bone)
								g.seek(tm+144)
							skeleton.draw()
							model.skeleton=skeleton.name
							for m in range(boneCount):
								model.boneNameList[skeleton.boneList[m].skinID]=skeleton.boneList[m].name
					if item2[0]==35:
						type3=g.B(1)[0]
						list3=getList(type3,g)
						boneCount=None
						for item3 in list3:
							g.seek(item3[1])
							#print item3
							if item3[0]==1:
								type4=g.B(1)[0]
								list4=getList(type4,g)
								for item4 in list4:
									g.seek(item4[1])
									flag=g.B(4)
									#print flag
									if flag==(160,0,65,0):
										type5=g.B(1)[0]
										list5=getList(type5,g)
										count=None
										for item5 in list5:
											g.seek(item5[1])
											if item5[0]==22:
												count=g.i(1)[0]
												#print count
											if item5[0]==23:
												streamOffset=g.tell()
										if count is not None:
											g.seek(streamOffset)
											model.boneMapList.append(g.i(count))

			elif flag == (0,0,161,0):
				pass#print 'audio clip'
			else:
				print 'unknow global flag:',flag,g.tell()

	for model in modelList:
		print 'model:',model.name
		i=0
		for meshChunk,matChunk in model.meshList:
			print ' '*4,meshChunk,matChunk
			mat=None
			for mat in matList:
				if mat.chunk==matChunk:
					break
			for mesh in meshList:
				if mesh.chunk==meshChunk:
					
					MAT=Mat()
					if mesh.TRIANGLE==True:MAT.TRIANGLE=True
					if mesh.TRISTRIP==True:MAT.TRISTRIP=True
					if mat is not None:

						if mat.diffChunk is not None:
							if mat.diffChunk in texList.keys():
								mat.diffuse=texList[mat.diffChunk]

						MAT.diffuse=mat.diffuse
					mesh.matList.append(MAT)
					mesh.boneNameList=model.boneNameList
					if i<len(model.boneMapList):
						skin=Skin()
						skin.boneMap=model.boneMapList[i]
						#print len(skin.boneMap)
						mesh.skinList.append(skin)

					mesh.BINDSKELETON=model.skeleton
					#print len(mesh.vertPosList),len(mesh.skinIndiceList),len(mesh.skinWeightList),len(mesh.boneNameList)
					#mesh.name=mesh.chunk
					#print mesh.name,mat.name
					try:mesh.draw()
					except:
						#print 'WARNING:mesh:',mesh.name
						pass
					break
			i+=1

def animFILEParser(filename,g):
	selObjectList=Blender.Object.GetSelected()
	if len(selObjectList)>0:
		armature=selObjectList[0]
		action=Action()
		action.skeleton=armature.name
		action.BONESPACE=True
		#action.ARMATURESPACE=True
		action.BONESORT=True
		action.UPDATE=False

		while(True):
			if g.tell()>=g.fileSize():break
			bone=ActionBone()
			action.boneList.append(bone)
			bone.name=g.find('\x00')
			#print bone.name
			count=g.i(1)[0]
			for m in range(count):
				frame=g.H(1)[0]
				bone.posFrameList.append(frame)
				bone.posKeyList.append(VectorMatrix(g.f(3)))
			count=g.i(1)[0]
			type=g.B(1)[0]
			if type==22:#not supported
				for m in range(count):
					bone.rotFrameList.append(m)
					x,y,z=g.short(3,'h',14)
					x=degrees(x)
					y=degrees(y)
					z=degrees(z)
					#print x,y,z
					bone.rotKeyList.append(Euler(x,y,z).toMatrix().resize4x4())
			if type==30:
				for m in range(count):
					bone.rotFrameList.append(m)
					bone.rotKeyList.append(QuatMatrix(g.short(4,'h',15)).resize4x4())

		action.draw()
		action.setContext()

def openFile(flagList):
	global input,output,txt
	input=Input(flagList)
	output=Output(flagList)
	filename=input.filename
	print
	print '='*70
	print filename
	print '='*70
	print
	ext=filename.split('.')[-1].lower()

	if ext=='prp':
		file=open(filename,'rb')
		g=BinaryReader(file)
		prpParser(filename,g)
		file.close()

	if ext=='anim':
		file=open(filename,'rb')
		g=BinaryReader(file)
		animFILEParser(filename,g)
		file.close()

Blender.Window.FileSelector(openFile,'import','Overlord I and II files: prp - archive, anim - animation')