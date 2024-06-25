import bpy
import Blender,os
from Blender.Mathutils import *

def	create_new_directory(new_directory_path):
	if os.path.exists(new_directory_path)==False:
		os.makedirs(new_directory_path)

def set_image_format(image_format,image):
	if image_format==7:
		image.format='DXT1'
	elif image_format==11:
		image.format='DXT5'
	elif image_format==9:
		image.format='DXT3'
	elif image_format==5:
		image.format='tga32'
	else:
		image.format=image_format
		print 'Warning: Unkown image_format : ',image_format,' for ',texture_name
	return image.format

def float255(data):
	list=[]
	for get in data:
		list.append(get/255.0)
	return list

def is_quat(quat):
	sum=quat[1]**2+quat[2]**2+quat[3]**2
	return quat[0]**2-sum

def quat_matrix(quat):
	return Quaternion(quat[3],quat[0],quat[1],quat[2]).toMatrix()

def vector_matrix(vector):
	return TranslationMatrix(Vector(vector))

def round_vector(vec,dec=17):
	fvec=[]
	for v in vec:
		fvec.append(round(v,dec))
	return Vector(fvec)

def round_matrix(mat,dec=17):
	fmat = []
	for row in mat:
		fmat.append(round_vector(row,dec))
	return Matrix(*fmat)

def matrix_4x4(data):
	return Matrix(	data[:4],\
					data[4:8],\
					data[8:12],\
					data[12:16])

def matrix_3x3(data):
	return Matrix(	data[:3],\
					data[3:6],\
					data[6:9])

def parse_id():
	ids = []
	scene = bpy.data.scenes.active
	for mat in Blender.Material.Get():
		try:
			model_id = int(mat.name.split('-')[0])
			ids.append(model_id)
		except:pass
	for object in scene.objects:
		if object.getType()=='Mesh':
			try:
				model_id = int(object.getData(mesh=1).name.split('-')[0])
				ids.append(model_id)
			except:pass
	for mesh in bpy.data.meshes:
			try:
				model_id = int(mesh.name.split('-')[0])
				ids.append(model_id)
			except:pass
	try:
		model_id = max(ids)+1
	except:
		model_id = 0
	return model_id

def set_blender_material_texture(blendMat,data,texture_type,short_type):
	if os.path.exists(getattr(data,texture_type))==True:
		image=Blender.Image.Load(getattr(data,texture_type))
		imgName=blendMat.name.replace('-mat-','-'+getattr(data,texture_type)+'-')
		image.setName(imgName)
		texture_name=blendMat.name.replace('-mat-','-'+getattr(data,texture_type)+'-')
		tex = Blender.Texture.New(texture_name)
		tex.setType('Image')
		if "normal" in texture_type:
			tex.setImageFlags('NormalMap')
		elif "alpha" in texture_type:
			tex.setImageFlags('CalcAlpha')
		tex.image = image
		
		if "normal" in texture_type:
			blendMat.setTexture(getattr(data,texture_type+'_slot'),tex,Blender.Texture.TexCo.UV,Blender.Texture.MapTo.NOR)
			blendMat.getTextures()[getattr(data,texture_type+'_slot')].norfac=getattr(data,texture_type+'_strong')
			blendMat.getTextures()[getattr(data,texture_type+'_slot')].mtNor=getattr(data,texture_type+'_direction')
			blendMat.getTextures()[getattr(data,texture_type+'_slot')].size=getattr(data,texture_type+'_size')
		elif "diffuse" in texture_type:
			if texture_type == "diffuse":
				blendMat.setTexture(data.diffuse_slot,tex,Blender.Texture.TexCo.UV,\
				Blender.Texture.MapTo.COL| Blender.Texture.MapTo.ALPHA|Blender.Texture.MapTo.CSP)
			else:
				blendMat.setTexture(getattr(data,texture_type+'_slot'),tex,Blender.Texture.TexCo.UV,\
				Blender.Texture.MapTo.COL|Blender.Texture.MapTo.CSP)
		elif "ambient_occlusion" in texture_type:
			blendMat.setTexture(data.ambient_occlusion_slot,tex,Blender.Texture.TexCo.UV,Blender.Texture.MapTo.COL)
			mtex=blendMat.getTextures()[data.ambient_occlusion_slot]
			mtex.blendmode=Blender.Texture.BlendModes.MULTIPLY
		elif "specular" in texture_type:
			blendMat.setTexture(data.specular_slot,tex,Blender.Texture.TexCo.UV,Blender.Texture.MapTo.CSP)
			mtextures = blendMat.getTextures()
			mtex=mtextures[data.specular_slot]
			mtex.neg=True
		elif "alpha" in texture_type:
			blendMat.setTexture(data.alpha_slot,tex,Blender.Texture.TexCo.UV,\
			Blender.Texture.MapTo.ALPHA)
			#blendMat.getTextures()[data.diffuse_slot].mtAlpha=0
		elif "reflection" in texture_type:
			blendMat.setTexture(data.reflection_slot,tex,Blender.Texture.TexCo.REFL,Blender.Texture.MapTo.COL)
			mtextures = blendMat.getTextures()
			mtex=mtextures[data.reflection_slot]
			mtex.colfac=data.reflection_strong