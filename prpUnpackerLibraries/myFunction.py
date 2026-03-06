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