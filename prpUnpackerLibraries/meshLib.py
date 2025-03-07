import bpy
import Blender
from Blender.Mathutils import *
from myFunction import *
import random

class Mesh():
	
	def __init__(self):
		self.vertice_position_list=[]
		self.vertice_normal_list=[]

		self.indice_list=[]
		self.face_list=[]
		self.triangle_list=[]

		self.material_list=[]
		self.material_id_list=[]
		self.vertice_uv_list=[]
		self.face_uv_list=[]

		self.skin_list=[]
		self.skin_weight_list=[]
		self.skin_indice_list=[]
		self.skin_id_list=[]
		self.bone_name_list=[]

		self.name=None
		self.object=None
		self.is_triangle=False
		self.is_quad=False
		self.is_triangle_strip=False
		self.bind_skeleton=None
		self.matrix=None
		self.split=False
		self.is_drawing_active=False
		self.uv_flip=False

	def add_vertex_uv(self,blenderMesh,mesh):
		blenderMesh.vertexUV = 1
		for m in range(len(blenderMesh.verts)):
			if self.uv_flip==False:
				blenderMesh.verts[m].uvco = Vector(mesh.vertice_uv_list[m][0],1-mesh.vertice_uv_list[m][1])
			else:
				blenderMesh.verts[m].uvco = Vector(mesh.vertice_uv_list[m])

	def add_face_uv(self,blenderMesh,mesh):
		if len(blenderMesh.faces)>0:
			blenderMesh.faceUV = 1
			if len(mesh.vertice_uv_list)>0:
				for ID in range(len(blenderMesh.faces)):
					face=blenderMesh.faces[ID]
					face.uv = [v.uvco for v in face.verts]
					face.smooth = 1
					if len(mesh.material_id_list)>0:
						face.mat=mesh.material_id_list[ID]
			if len(mesh.material_id_list)>0:
				for ID in range(len(blenderMesh.faces)):
					face=blenderMesh.faces[ID]
					face.smooth = 1
					face.mat=mesh.material_id_list[ID]
			if len(mesh.face_uv_list)>0:
				for ID in range(len(blenderMesh.faces)):
					face=blenderMesh.faces[ID]
					if mesh.face_uv_list[ID] is not None:
						face.uv=mesh.face_uv_list[ID]
			if len(self.vertice_normal_list)==0:
				blenderMesh.calcNormals()
			blenderMesh.update()

	def add_skin_id_list(self):
		if len(self.skin_id_list)==0:
			for skinID in range(len(self.skin_list)):
				skin=self.skin_list[skinID]
				if skin.id_start==None:
					skin.id_start=0
				if skin.id_count==None:
					skin.id_count=len(self.skin_indice_list)
				for vertID in range(skin.id_count):
					self.skin_id_list.append(skinID)

	def add_skin(self,blendMesh,mesh):

		for vertID in range(len(mesh.skin_id_list)):
			indices=mesh.skin_indice_list[vertID]
			weights=mesh.skin_weight_list[vertID]
			skinID=mesh.skin_id_list[vertID]
			for n in range(len(indices)):
				w  = weights[n]
				if type(w)==int:w=w/255.0
				if w!=0:
					grID = indices[n]
					if len(self.bone_name_list)==0:
						if len(self.skin_list[skinID].bone_map)>0:
							grName = str(self.skin_list[skinID].bone_map[grID])
						else:
							grName = str(grID)
					else:
						if len(self.skin_list[skinID].bone_map)>0:
							grNameID = self.skin_list[skinID].bone_map[grID]
							grName=self.bone_name_list[grNameID]
						else:
							grName=self.bone_name_list[grID]
					if grName not in blendMesh.getVertGroupNames():
						blendMesh.addVertGroup(grName)
					blendMesh.assignVertsToGroup(grName,[vertID],w,1)
		blendMesh.update()

	def add_faces(self):
		if len(self.material_list)==0:
			if len(self.face_list)!=0:
				self.triangle_list=self.face_list
			if len(self.indice_list)!=0:
				if self.is_triangle==True:
					self.indices_to_triangles(self.indice_list,0)
				elif self.is_quad==True:
					self.indices_to_quads(self.indice_list,0)
				elif self.is_triangle_strip==True:
					self.indices_to_triangle_strips(self.indice_list,0)

		else:
			if len(self.face_list)>0:
				if len(self.material_id_list)==0:
					for matID in range(len(self.material_list)):
						mat=self.material_list[matID]
						if mat.id_start is not None and mat.id_count is not None:
							for faceID in range(mat.id_count):
								self.triangle_list.append(self.face_list[mat.id_start+faceID])
								self.material_id_list.append(matID)
						else:
							if mat.id_start==None:
								mat.id_start=0
							if mat.id_count==None:
								mat.id_count=len(self.face_list)
							for faceID in range(mat.id_count):
								self.triangle_list.append(self.face_list[mat.id_start+faceID])
								self.material_id_list.append(matID)
					#self.triangle_list=self.face_list

				else:
					self.triangle_list=self.face_list
					#for ID in range(len(self.material_id_list)):
					#	mat=self.material_list[matID] 
						#if self.material_id_list[ID]==matID:
					#	self.triangle_list.append(self.face_list[ID])

			if len(self.indice_list)>0:
				for matID in range(len(self.material_list)):
					mat=self.material_list[matID]
					if mat.id_start==None:
						mat.id_start=0
					if mat.id_count==None:
						mat.id_count=len(self.indice_list)
					indice_list=self.indice_list[mat.id_start:mat.id_start+mat.id_count]
					if mat.is_triangle==True:
						self.indices_to_triangles(indice_list,matID)
					elif mat.is_quad==True:
						self.indices_to_quads(indice_list,matID)
					elif mat.is_triangle_strip==True:
						self.indices_to_triangle_strips(indice_list,matID)

	def build_mesh(self,mesh,mat,meshID):
		blendMesh = bpy.data.meshes.new(mesh.name)
		blendMesh.verts.extend(mesh.vertice_position_list)
		blendMesh.faces.extend(mesh.triangle_list)
		blendMesh.materials+=[mat.get_blender_material(mesh.name,meshID)]
		if len(mesh.triangle_list)>0:
			if len(mesh.vertice_uv_list)>0:
				self.add_vertex_uv(blendMesh,mesh)
				self.add_face_uv(blendMesh,mesh)
			if len(mesh.face_uv_list)>0:
				self.add_face_uv(blendMesh,mesh)
		if len(mesh.vertice_normal_list)>0:
			for i,vert in enumerate(blendMesh.verts):
				vert.no=Vector(self.vertice_normal_list[i])

		scene = bpy.data.scenes.active
		meshobject = scene.objects.new(blendMesh,mesh.name)
		self.add_skin(blendMesh,mesh)
		Blender.Window.RedrawAll()
		if self.bind_skeleton is not None:
			for object in scene.objects:
				if object.name==self.bind_skeleton:
					#meshobject.mat*=object.mat
					object.makeParentDeform([meshobject],1,0)
		if self.matrix is not None:
			meshobject.setMatrix(self.matrix*meshobject.matrixWorld)
		Blender.Window.RedrawAll()

	def add_mesh(self):
		self.mesh = bpy.data.meshes.new(self.name)
		self.mesh.verts.extend(self.vertice_position_list)
		if len(self.vertice_normal_list)>0:
			for i,vert in enumerate(self.mesh.verts):
				vert.no=Vector(self.vertice_normal_list[i])

		self.mesh.faces.extend(self.triangle_list,ignoreDups=True)
		scene = bpy.data.scenes.active
		self.object = scene.objects.new(self.mesh,self.name)

	def draw(self):
		if self.name is None:self.name=str(parse_id())+'-model-'+str(0)
		self.add_faces()
		self.add_skin_id_list()

		if self.split==False:
			self.add_mesh()
			if len(self.triangle_list)>0:
				if len(self.vertice_uv_list)>0:
					self.add_vertex_uv(self.mesh,self)
			self.add_face_uv(self.mesh,self)
			for matID in range(len(self.material_list)):
				mat=self.material_list[matID]
				self.mesh.materials+=[mat.get_blender_material(self.mesh.name,matID)]

			if self.bind_skeleton is not None:
				scene = bpy.data.scenes.active
				for object in scene.objects:
					if object.name==self.bind_skeleton:
						skeletonMatrix=self.object.getMatrix()*object.mat
						object.makeParentDeform([self.object],1,0)
			self.add_skin(self.mesh,self)

			if self.matrix is not None:
				self.object.setMatrix(self.matrix*self.object.matrixWorld)
			Blender.Window.RedrawAll()

		if self.split==True:
			mesh_list=[]
			for matID in range(len(self.material_list)):
				mesh=Mesh()
				mesh.idList={}
				mesh.id=0
				mesh.name=self.name+'-'+str(matID)
				mesh_list.append(mesh)
				for n in range(len(self.vertice_position_list)):
					mesh.idList[str(n)]=None

			for faceID in range(len(self.material_id_list)):
				matID=self.material_id_list[faceID]
				mesh=mesh_list[matID]
				face=[]
				for v in range(len(self.triangle_list[faceID])):
					vid=self.triangle_list[faceID][v]
					if mesh.idList[str(vid)]==None:
						mesh.idList[str(vid)]=mesh.id
						mesh.vertice_position_list.append(self.vertice_position_list[vid])
						if len(self.vertice_uv_list)>0:
							mesh.vertice_uv_list.append(self.vertice_uv_list[vid])
						if len(self.vertice_normal_list)>0:
							mesh.vertice_normal_list.append(self.vertice_normal_list[vid])
						if len(self.skin_indice_list)>0 and len(self.skin_weight_list)>0:
							mesh.skin_weight_list.append(self.skin_weight_list[vid])
							mesh.skin_indice_list.append(self.skin_indice_list[vid])
							mesh.skin_id_list.append(self.skin_id_list[vid])
						face.append(mesh.id)
						mesh.id+=1
					else:
						oldid=mesh.idList[str(vid)]
						face.append(oldid)
				mesh.triangle_list.append(face)
				if len(self.face_uv_list)>0:
					mesh.face_uv_list.append(self.face_uv_list[faceID])
				mesh.material_id_list.append(0)

			for meshID in range(len(mesh_list)):
				mesh=mesh_list[meshID]
				mat=self.material_list[meshID]
				self.build_mesh(mesh,mat,meshID)
			Blender.Window.RedrawAll()

	def indices_to_quads(self,indicesList,matID):
		for m in range(0, len(indicesList), 4):
			self.triangle_list.append(indicesList[m:m+4] )
			self.material_id_list.append(matID)

	def indices_to_triangles(self,indicesList,matID):
		for m in range(0, len(indicesList), 3):
			self.triangle_list.append(indicesList[m:m+3] )
			self.material_id_list.append(matID)

	def indices_to_triangle_strips(self,indicesList,matID):
		StartDirection = -1
		id=0
		f1 = indicesList[id]
		id+=1
		f2 = indicesList[id]
		FaceDirection = StartDirection
		while(True):
			id+=1
			f3 = indicesList[id]
			if (f3==0xFFFF):
				if id==len(indicesList)-1:
					break
				id+=1
				f1 = indicesList[id]
				id+=1
				f2 = indicesList[id]
				FaceDirection = StartDirection
			else:
				FaceDirection *= -1
				if (f1!=f2) and (f2!=f3) and (f3!=f1):
					if FaceDirection > 0:
						self.triangle_list.append([(f1),(f2),(f3)])
						self.material_id_list.append(matID)
					else:
						self.triangle_list.append([(f1),(f3),(f2)])
						self.material_id_list.append(matID)
					if self.is_drawing_active==True:
						f1,f2,f3
				f1 = f2
				f2 = f3
			if id==len(indicesList)-1:
				break

class Skin:
	def __init__(self):
		self.bone_map=[]
		self.id_start=None
		self.id_count=None

class Mat:
	def __init__(self):#0,1,2,3,4,5,6,7,
		self.name=None
		self.texture_file=None
		self.ztrans=False

		self.diffuse=None
		self.diffuse_slot=0

		self.diffuse1=None
		self.diffuse1_slot=6
		self.diffuse2=None
		self.diffuse2_slot=7
		self.alpha=None
		self.alpha_slot=8

		self.normal=None
		self.normal_slot=1
		self.normal_strong=0.5
		self.normal_direction=1
		self.normal_size=(1,1,1)

		self.specular=None
		self.specular_slot=2

		self.ambient_occlusion=None
		self.ambient_occlusion_slot=3

		self.normal1=None
		self.normal1_slot=4
		self.normal1_strong=0.8
		self.normal1_direction=1
		self.normal1_size=(15,15,15)

		self.normal2=None
		self.normal2_slot=5
		self.normal2_strong=0.8
		self.normal2_direction=1
		self.normal2_size=(15,15,15)

		self.reflection=None
		self.reflection_slot=8
		self.reflection_strong=1.0

		self.is_triangle=False
		self.is_triangle_strip=False
		self.is_quad=False
		self.id_start=None
		self.id_count=None

		red=random.randint(0,255)
		green=random.randint(0,255)
		blue=random.randint(0,255)
		self.rgba=[red/255.0,green/255.0,blue/255.0,1.0]

	def get_blender_material(self,mesh_name,ID):
		if self.name is None:
			self.name=mesh_name+'-mat-'+str(ID)
		blendMat=Blender.Material.New(self.name)
		blendMat.diffuseShader=Blender.Material.Shaders.DIFFUSE_ORENNAYAR
		blendMat.specShader=Blender.Material.Shaders.SPEC_WARDISO
		blendMat.setRms(0.04)
		blendMat.shadeMode=Blender.Material.ShadeModes.CUBIC
		blendMat.rgbCol=self.rgba[:3]
		blendMat.alpha = self.rgba[3]
		if self.ztrans==True:
			blendMat.mode |= Blender.Material.Modes.ZTRANSP
			blendMat.mode |= Blender.Material.Modes.TRANSPSHADOW
			blendMat.alpha = 0.0
		if self.diffuse is not None:
			set_blender_material_texture(blendMat,self,"diffuse","diff")
		if self.reflection is not None:
			set_blender_material_texture(blendMat,self,"reflection","refl")
		if self.diffuse1 is not None:
			set_blender_material_texture(blendMat,self,"diffuse1","diff")
		if self.diffuse2 is not None:
			set_blender_material_texture(blendMat,self,"diffuse2","diff")
		if self.specular is not None:
			set_blender_material_texture(blendMat,self,"specular","spec")
		if self.normal is not None:
			set_blender_material_texture(blendMat,self,"normal","norm")
		if self.normal1 is not None:
			set_blender_material_texture(blendMat,self,"normal1","norm")
		if self.normal2 is not None:
			set_blender_material_texture(blendMat,self,"normal2","norm")
		if self.ambient_occlusion is not None:
			set_blender_material_texture(blendMat,self,"ambient_occlusion","ao")
		if self.alpha is not None:
			set_blender_material_texture(blendMat,self,"alpha","alpha")

		return blendMat