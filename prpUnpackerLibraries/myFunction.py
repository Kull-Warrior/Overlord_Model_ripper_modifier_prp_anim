import bpy
import Blender,os
from Blender.Mathutils import *

def	create_new_directory(new_directory_path):
	if os.path.exists(new_directory_path)==False:
		os.makedirs(new_directory_path)

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
		#print mat.name
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