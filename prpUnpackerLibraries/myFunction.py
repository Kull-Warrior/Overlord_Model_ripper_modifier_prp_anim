import bpy
import os
import mathutils
from mathutils import Quaternion, Vector, Matrix

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
	elif image_format==3:
		image.format='tga24'
	else:
		image.format=image_format
		print ('Warning: Unkown image_format : ',image_format,' for ',texture_name)
	return image.format

def is_quat(quat):
	sum=quat[1]**2+quat[2]**2+quat[3]**2
	return quat[0]**2-sum

def quat_matrix(quat):
    # Create a Quaternion from a list or tuple and convert it to a 3x3 rotation matrix
    return Quaternion(quat).to_matrix()

def vector_matrix(vector):
    # Create a translation matrix from a vector
    return Matrix.Translation(Vector(vector))

def round_vector(vec, dec=17):
    # Round each component of the vector to the specified number of decimal places
    return Vector([round(v, dec) for v in vec])

def round_matrix(mat, dec=17):
    # Round each element of the matrix to the specified number of decimal places
    return Matrix([round_vector(row, dec) for row in mat])

def matrix_4x4(data):
    # Create a 4x4 matrix from a flat list of 16 elements
    return Matrix([data[i:i+4] for i in range(0, 16, 4)])

def parse_id():
	ids = []
	scene = bpy.data.scenes.active
	for mat in Blender.Material.Get():
		try:
			model_id = int(mat.name.split('-')[0])
			ids.append(model_id)
		except:
			pass
	for object in scene.objects:
		if object.getType()=='Mesh':
			try:
				model_id = int(object.getData(mesh=1).name.split('-')[0])
				ids.append(model_id)
			except:
				pass
	for mesh in bpy.data.meshes:
			try:
				model_id = int(mesh.name.split('-')[0])
				ids.append(model_id)
			except:
				pass
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

def safe(count):
	return count<100000

def get_title(file_reader):
	file_reader.seek(16)
	return file_reader.read_string(160)

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

def add_leading_zeros(counter):
	string=""
	if counter<100:
		string+="0"
	if counter<10:
		string+="0"
	return string