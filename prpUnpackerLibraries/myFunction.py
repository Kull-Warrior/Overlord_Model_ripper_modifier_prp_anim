import bpy
import Blender,os
from Blender.Mathutils import *
import types

class Input(object):
	def __init__(self,flagList):
		self.flagList=flagList
		self.type=None
		self.debug=None
		if type(flagList)==types.InstanceType:
			self.type='instance'
			self.filename=flagList.assetPath
			self.imageList=flagList.pluginList[flagList.pluginName]['imageList']
			self.model_list=flagList.pluginList[flagList.pluginName]['model_list']
			self.animList=flagList.pluginList[flagList.pluginName]['animList']
			self.archiveList=flagList.pluginList[flagList.pluginName]['archiveList']
			self.output=flagList
			self.returnList=self.flagList.returnList
			self.returnKey=self.flagList.returnKey
		if type(flagList)==types.StringType:
			self.type='string'
			self.filename=flagList
			self.imageList=[]
			self.model_list=[]
			self.animList=[]
			self.archiveList=[]

def input1(object):
	return object

def output(object):
	return object

def float255(data):
	list=[]
	for get in data:
		list.append(get/255.0)
	return list

class Sys(object):
	def __init__(self,input):
		self.input=input
		if '.' in os.path.basename(input):
			self.ext=os.path.basename(input).split('.')[-1]
		else:
			self.ext=''
		if '.' in os.path.basename(input):
			self.base=os.path.basename(input).split('.'+self.ext)[0]
		else:
			self.base=os.path.basename(input)+'Dir'
		self.dir=os.path.dirname(input)
		self.blendFile=Blender.Get('filename')
	def	add_directory(self,base):
		newDir=self.dir+os.sep+base
		if os.path.exists(newDir)==False:
			os.makedirs(newDir)

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

class Searcher():
	def __init__(self):
		self.dir=None
		self.list=[]
		self.what=None
	def run(self):
		dir=self.dir
		def tree(dir):
			list_dir = os.listdir(dir)
			olddir = dir
			for m in list_dir:
				if self.what.lower() in m.lower():
					self.list.append(olddir+os.sep+m)
				if os.path.isdir(olddir+os.sep+m)==True:
					dir = olddir+os.sep+m
					tree(dir)
		tree(dir)

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