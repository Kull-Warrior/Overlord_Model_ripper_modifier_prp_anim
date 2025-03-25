import bpy
import bmesh
from mathutils import Vector, Matrix
import os
import random

# -----------------------------------------------------------------------------
# Helper Function: parse_id
# -----------------------------------------------------------------------------
def parse_id():
	"""
	Generates a new unique numerical ID based on existing material, object, and mesh names.
	It assumes that names start with a number followed by a hyphen (e.g., '5-modelName').
	"""
	ids = []
	# Check materials
	for mat in bpy.data.materials:
		try:
			model_id = int(mat.name.split('-')[0])
			ids.append(model_id)
		except Exception:
			pass
	# Check objects (only Mesh objects)
	for obj in bpy.data.objects:
		if obj.type == 'MESH':
			try:
				model_id = int(obj.data.name.split('-')[0])
				ids.append(model_id)
			except Exception:
				pass
	# Check all mesh data blocks
	for mesh in bpy.data.meshes:
		try:
			model_id = int(mesh.name.split('-')[0])
			ids.append(model_id)
		except Exception:
			pass
	try:
		new_id = max(ids) + 1
	except Exception:
		new_id = 0
	return new_id

# -----------------------------------------------------------------------------
# Class: Mesh
# -----------------------------------------------------------------------------
class Mesh:
	def __init__(self):
		# Geometry data
		self.vertice_position_list = []  # List of Vector positions
		self.indice_list = []            # Raw index list (could be triangles or strips)
		self.triangle_list = []          # List of triangles (each a list of 3 vertex indices)
		
		# Material and UV data
		self.material_list = []          # List of Mat objects
		self.material_id_list = []       # Per-face material assignments
		self.vertice_uv_list = []        # UV coordinates per vertex
		
		# Skinning data
		self.skin_list = []              # List of Skin objects
		self.skin_weight_list = []       # Skin weights per vertex (list of floats or lists)
		self.skin_indice_list = []       # Skin bone indices per vertex
		self.skin_id_list = []           # For each vertex, which skin applies
		self.bone_name_list = []         # List of bone names for vertex groups
		
		# Other properties
		self.name = None                 # Name of the mesh
		self.object = None               # The Blender object created from this mesh
		self.is_triangle = False         # Flag: if indices are triangles
		self.is_triangle_strip = False   # Flag: if indices are triangle strips
		self.bind_skeleton = None        # Name of the armature for skinning
		self.matrix = None               # Transformation matrix (Matrix)
		self.uv_flip = False             # Whether to flip UV vertically

	def add_vertex_uv(self, mesh_data):
		"""
		Create a UV map and assign UV coordinates to each vertex in each face loop.
		"""
		if not mesh_data.uv_layers:
			uv_layer = mesh_data.uv_layers.new(name="UVMap")
		else:
			uv_layer = mesh_data.uv_layers.active

		# In Blender 2.8+, UVs are stored per loop (corner of each face).
		for poly in mesh_data.polygons:
			for li in poly.loop_indices:
				vert_index = mesh_data.loops[li].vertex_index
				if vert_index < len(self.vertice_uv_list):
					u, v = self.vertice_uv_list[vert_index]
					if not self.uv_flip:
						uv_layer.data[li].uv = (u, 1 - v)
					else:
						uv_layer.data[li].uv = (u, v)

	def add_face_uv(self, mesh_data):
		"""
		Update normals and refresh mesh data.
		"""
		mesh_data.validate()  # Validate the mesh geometry
		mesh_data.update()    # Update the mesh data
		mesh_data.calc_normals_split()

	def add_skin_id_list(self):
		"""
		Initialize the skin_id_list based on the skins in skin_list.
		"""
		if not self.skin_id_list:
			for skinID, skin in enumerate(self.skin_list):
				if skin.id_start is None:
					skin.id_start = 0
				if skin.id_count is None:
					skin.id_count = len(self.skin_indice_list)
				for _ in range(skin.id_count):
					self.skin_id_list.append(skinID)

	def add_skin(self, obj):
		"""
		Assigns vertex groups (bone weights) to the given object based on skin data.
		"""
		for vertID in range(len(self.skin_id_list)):
			indices = self.skin_indice_list[vertID]
			weights = self.skin_weight_list[vertID]
			skinID = self.skin_id_list[vertID]
			for n, w in enumerate(weights):
				# Normalize weight if stored as int
				if isinstance(w, int):
					w = w / 255.0
				if w != 0:
					grID = indices[n]
					if not self.bone_name_list:
						if self.skin_list[skinID].bone_map:
							grName = str(self.skin_list[skinID].bone_map[grID])
						else:
							grName = str(grID)
					else:
						if self.skin_list[skinID].bone_map:
							grNameID = self.skin_list[skinID].bone_map[grID]
							grName = self.bone_name_list[grNameID]
						else:
							grName = self.bone_name_list[grID]
					# Create vertex group if it doesn't exist
					if grName not in obj.vertex_groups:
						obj.vertex_groups.new(name=grName)
					group = obj.vertex_groups[grName]
					group.add([vertID], w, 'REPLACE')

	def indices_to_triangles(self, indices_list, matID):
		"""
		Converts a flat list of indices into triangles (3 indices per face).
		"""
		for i in range(0, len(indices_list), 3):
			face = indices_list[i:i+3]
			if len(face) == 3:
				self.triangle_list.append(face)
				self.material_id_list.append(matID)

	def indices_to_triangle_strips(self, indices_list, matID):
		"""
		Converts a triangle strip (compact representation) into individual triangles.
		"""
		start_direction = -1
		idx = 0
		if idx < len(indices_list):
			f1 = indices_list[idx]
			idx += 1
		if idx < len(indices_list):
			f2 = indices_list[idx]
			idx += 1
		face_direction = start_direction
		while idx < len(indices_list):
			f3 = indices_list[idx]
			if f3 == 0xFFFF:
				idx += 1
				if idx >= len(indices_list):
					break
				f1 = indices_list[idx]
				idx += 1
				if idx >= len(indices_list):
					break
				f2 = indices_list[idx]
				face_direction = start_direction
			else:
				face_direction *= -1
				if f1 != f2 and f2 != f3 and f3 != f1:
					if face_direction > 0:
						self.triangle_list.append([f1, f2, f3])
					else:
						self.triangle_list.append([f1, f3, f2])
					self.material_id_list.append(matID)
				f1, f2 = f2, f3
			idx += 1

	def add_faces(self):
		"""
		Converts raw indice_list into triangle_list based on face type and material assignment.
		"""
		if not self.material_list:
			if self.indice_list:
				if self.is_triangle:
					self.indices_to_triangles(self.indice_list, 0)
				elif self.is_triangle_strip:
					self.indices_to_triangle_strips(self.indice_list, 0)
		else:
			if self.indice_list:
				for matID, mat in enumerate(self.material_list):
					if mat.id_start is None:
						mat.id_start = 0
					if mat.id_count is None:
						mat.id_count = len(self.indice_list)
					indices = self.indice_list[mat.id_start:mat.id_start + mat.id_count]
					if mat.is_triangle:
						self.indices_to_triangles(indices, matID)
					elif mat.is_triangle_strip:
						self.indices_to_triangle_strips(indices, matID)

	def add_mesh(self):
		"""
		Creates a new Blender mesh from the vertex and face data,
		links it to the current collection, and stores the object reference.
		"""
		mesh_data = bpy.data.meshes.new(self.name)
		mesh_data.from_pydata(self.vertice_position_list, [], self.triangle_list)
		mesh_data.update()
		obj = bpy.data.objects.new(self.name, mesh_data)
		bpy.context.collection.objects.link(obj)
		self.object = obj

	def draw(self):
		"""
		Draws the mesh in Blender:
		- Converts indices to faces
		- Creates a new mesh object
		- Adds UVs and materials
		- Parents to an armature if needed
		- Applies vertex groups and modifiers
		"""
		
		if self.name is None:
			self.name = f"{parse_id()}-model-0"

		self.add_faces()
		self.add_skin_id_list()
		self.add_mesh()

		# Add UVs if they exist
		if self.triangle_list and self.vertice_uv_list:
			self.add_vertex_uv(self.object.data)
		self.add_face_uv(self.object.data)

		# Assign materials
		for matID, mat in enumerate(self.material_list):
			blender_mat = mat.get_blender_material(self.name, matID)
			self.object.data.materials.append(blender_mat)

			# Assign material index to each polygon
			for poly in self.object.data.polygons:
				if poly.index < len(self.material_id_list):
					poly.material_index = self.material_id_list[poly.index]

		# Parent to an armature if bind_skeleton is specified
		if self.bind_skeleton is not None:
			arm_obj = bpy.data.objects.get(self.bind_skeleton)
			if arm_obj and arm_obj.type == 'ARMATURE':
				if not self.object.users_collection:
					bpy.context.collection.objects.link(self.object)
					
				# Set parent and update the parent inverse matrix
				self.object.parent = arm_obj
				self.object.matrix_parent_inverse = arm_obj.matrix_world.inverted()

				# Add an Armature modifier if not already present
				if "ArmatureMod" not in self.object.modifiers:
					armature_mod = self.object.modifiers.new(name="ArmatureMod", type='ARMATURE')
					armature_mod.object = arm_obj

		# **Apply vertex groups (skinning)**
		self.add_skin(self.object)

		# **Apply transformation matrix**
		if self.matrix is not None:
			self.object.matrix_world = self.matrix @ self.object.matrix_world

		# **Force Blender to update scene**
		bpy.context.view_layer.update()

# -----------------------------------------------------------------------------
# Class: Skin
# -----------------------------------------------------------------------------
class Skin:
	def __init__(self):
		self.bone_map = []   # Mapping from local skin indices to bone names or indices
		self.id_start = None # Starting vertex index for this skin (optional)
		self.id_count = None # Number of vertices influenced by this skin

# -----------------------------------------------------------------------------
# Helper Function: set_material_texture
# -----------------------------------------------------------------------------
def set_material_texture(mat, texture_path, node_label):
	"""
	Loads an image from a file and creates an image texture node in the material's node tree.
	Returns the created node if successful.
	"""
	if os.path.exists(texture_path):
		img = bpy.data.images.load(texture_path)
		image_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
		image_node.image = img
		image_node.label = node_label
		return image_node
	return None

# -----------------------------------------------------------------------------
# Class: Mat (Material)
# -----------------------------------------------------------------------------
class Mat:
	def __init__(self):
		self.name = None
		self.texture_file = None
		self.ztrans = False

		self.diffuse = None
		self.diffuse_slot = 0

		self.normal = None
		self.normal_slot = 1
		self.normal_strong = 0.5
		self.normal_direction = 1
		self.normal_size = (1, 1, 1)

		self.specular = None
		self.specular_slot = 2

		self.reflection = None
		self.reflection_slot = 8
		self.reflection_strong = 1.0

		self.is_triangle = False
		self.is_triangle_strip = False
		self.id_start = None
		self.id_count = None

		# Generate a random diffuse color
		red = random.randint(0, 255)
		green = random.randint(0, 255)
		blue = random.randint(0, 255)
		self.rgba = [red / 255.0, green / 255.0, blue / 255.0, 1.0]

	def get_blender_material(self, mesh_name, ID):
		"""
		Creates a new Blender material using the Principled BSDF shader.
		Applies a diffuse texture if provided.
		"""
		if self.name is None:
			self.name = f"{mesh_name}-mat-{ID}"
		mat = bpy.data.materials.new(name=self.name)
		mat.use_nodes = True
		nodes = mat.node_tree.nodes
		links = mat.node_tree.links

		# Remove default nodes
		for node in nodes:
			nodes.remove(node)
		# Create shader nodes
		output_node = nodes.new(type='ShaderNodeOutputMaterial')
		output_node.location = (300, 0)
		principled = nodes.new(type='ShaderNodeBsdfPrincipled')
		principled.location = (0, 0)
		principled.inputs['Base Color'].default_value = (*self.rgba[:3], 1)
		links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])

		# Example: if diffuse texture is provided, load it and link to Base Color
		if self.diffuse is not None:
			tex_image = set_material_texture(mat, self.diffuse, "Diffuse")
			if tex_image:
				links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])

		return mat