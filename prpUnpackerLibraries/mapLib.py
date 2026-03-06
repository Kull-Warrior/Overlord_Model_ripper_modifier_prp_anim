import bpy
import math
import numpy as np

class OverlordMap:
	def __init__(self):
		# Initialize 512x512 arrays for all maps
		self.HeightMapDigitsOneAndTwo = np.zeros((512, 512), dtype=np.uint8)
		self.HeightMapDigitsThreeAndFour = np.zeros((512, 512), dtype=np.uint8)
		self.MainTextureMap = np.zeros((512, 512), dtype=np.uint8)
		self.FoliageMap = np.zeros((512, 512), dtype=np.uint8)
		self.WallTextureMap = np.zeros((512, 512), dtype=np.uint8)
		self.UnknownMap = np.zeros((512, 512), dtype=np.uint8)
		self.lua_bytecode_list=[]
		self.water_level=0
		self.rpk_resources=[]
		self.texture_atlas=None

	def set_map_data(self, data: bytes):
		"""Equivalent of C# SetMapData with vectorized NumPy operations"""
		# Convert byte data to NumPy array
		data_np = np.frombuffer(data, dtype=np.uint8)
		
		# Reshape to [y, x, 4] and transpose to [x, y, 4]
		data_3d = data_np.reshape(512, 512, 4).transpose(1, 0, 2)
		
		# Extract and process data using vectorized operations
		self.HeightMapDigitsOneAndTwo = data_3d[:, :, 0]
		self.HeightMapDigitsThreeAndFour = data_3d[:, :, 1]
		self.MainTextureMap = data_3d[:, :, 2] & 0x0F
		self.FoliageMap = (data_3d[:, :, 2] & 0xF0) >> 4
		self.WallTextureMap = data_3d[:, :, 3] & 0x0F
		self.UnknownMap = (data_3d[:, :, 3] & 0xF0) >> 4

	def get_float_map(self) -> np.ndarray:
		"""Equivalent of C# GetFloatMap with vectorized NumPy operations"""
		# Extract components using bitwise operations
		highest_digit = (self.HeightMapDigitsThreeAndFour & 0x0F) * 16.0  # 16^1
		middle_digit = ((self.HeightMapDigitsOneAndTwo & 0xF0) >> 4) * 1.0  # 16^0
		smallest_digit = (self.HeightMapDigitsOneAndTwo & 0x0F) * 0.0625  # 16^-1
		
		# Combine and scale, then convert to float32
		float_map = (highest_digit + middle_digit + smallest_digit) / 2.0
		return float_map.astype(np.float32)

	def create_material(self, obj):
		"""
		Create a single material using the texture atlas.
		"""
		# Clear any existing materials
		obj.data.materials.clear()

		mat = bpy.data.materials.new(name="TerrainAtlasMat")
		mat.use_nodes = True
		nodes = mat.node_tree.nodes
		links = mat.node_tree.links

		# Clear default nodes
		for node in nodes:
			nodes.remove(node)

		# Create nodes
		tex_coord = nodes.new(type="ShaderNodeTexCoord")
		mapping = nodes.new(type="ShaderNodeMapping")
		tex_image = nodes.new(type="ShaderNodeTexImage")
		bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
		output = nodes.new(type="ShaderNodeOutputMaterial")

		# Load texture atlas
		try:
			tex_image.image = self.texture_atlas
		except Exception as e:
			print(f"Error loading texture atlas: {e}")

		# Link nodes
		links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
		links.new(mapping.outputs["Vector"], tex_image.inputs["Vector"])
		links.new(tex_image.outputs["Color"], bsdf.inputs["Base Color"])
		links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

		# Position nodes (optional)
		tex_coord.location = (-500, 0)
		mapping.location = (-250, 0)
		tex_image.location = (0, 0)
		bsdf.location = (500, 0)
		output.location = (1000, 0)

		# Assign material to object
		obj.data.materials.append(mat)

	def create_full_terrain_scene(self, name="Terrain", scale=1.0, vertical_scale=1.0, center_mesh=True):
		"""Create the terrain mesh with UVs mapped to the texture atlas."""
		height_data = self.get_float_map()
		
		# Clear existing objects
		bpy.ops.object.select_all(action='SELECT')
		bpy.ops.object.delete()

		# Create vertices with scaling
		vertices = []
		for i in range(512):
			for j in range(512):
				x = j * scale
				y = i * scale
				z = height_data[i][j] * vertical_scale
				vertices.append((x, y, z))

		# Create faces
		faces = []
		for i in range(511):
			for j in range(511):
				v1 = i * 512 + j
				v2 = v1 + 512
				v3 = v2 + 1
				v4 = v1 + 1
				faces.append((v1, v2, v3, v4))

		# Create mesh and object
		mesh = bpy.data.meshes.new(name)
		obj = bpy.data.objects.new(name, mesh)
		mesh.from_pydata(vertices, [], faces)
		mesh.validate()
		mesh.update()
		
		# Center mesh if requested
		if center_mesh:
			obj.location = (-256 * scale, -256 * scale, 0)

		# Add to scene
		bpy.context.collection.objects.link(obj)
		bpy.context.view_layer.objects.active = obj
		obj.select_set(True)

		# Create UV layer and assign coordinates based on MainTextureMap
		uv_layer = mesh.uv_layers.new(name="AtlasUV").data

		for face in mesh.polygons:
			face_index = face.index
			i = face_index // 511  # Row in 511x511 grid
			j = face_index % 511   # Column in grid
			texture_id = int(self.MainTextureMap[i, j])
			texture_id = max(0, min(15, texture_id))  # Clamp to 0-15

			# Calculate tile coordinates (4x4 grid)
			tile_size = 0.25
			column = texture_id % 4
			row = texture_id // 4
			u_min = column * tile_size
			v_min = (3 - row) * tile_size  # Invert row for top-left origin
			u_max = u_min + tile_size
			v_max = v_min + tile_size

			# Assign UVs to each loop (vertex) of the face
			loops = face.loop_indices
			uv_layer[loops[0]].uv = (u_min, v_max)  # Upper-left corner of tile
			uv_layer[loops[1]].uv = (u_min, v_min)  # Lower-left corner
			uv_layer[loops[2]].uv = (u_max, v_min)  # Lower-right corner
			uv_layer[loops[3]].uv = (u_max, v_max)  # Upper-right corner

		# Set up lighting and camera (unchanged)
		bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 100))
		sun = bpy.context.active_object
		sun.data.energy = 0.25

		# Create camera
		bpy.ops.object.camera_add(location=(300, -300, 300))
		camera = bpy.context.active_object
		camera.rotation_euler = (math.radians(60), 0, math.radians(45))
		bpy.context.scene.camera = camera

		# Set up viewport shading
		for area in bpy.context.screen.areas:
			if area.type == 'VIEW_3D':
				for space in area.spaces:
					if space.type == 'VIEW_3D':
						space.shading.type = 'MATERIAL'
						space.shading.use_scene_lights = True

		# Set background lighting
		bpy.context.scene.world.use_nodes = True
		world_nodes = bpy.context.scene.world.node_tree.nodes
		world_nodes["Background"].inputs[1].default_value = 0.2  # Ambient light

		# Create and assign the single material
		self.create_material(obj)

		return obj

	def create_water_plane(self, name="WaterPlane"):
		# Create plane primitive
		# Create grid with proper resolution to maintain square shape
		bpy.ops.mesh.primitive_grid_add(
			size=512,  # Total width/length
			x_subdivisions=128,  # Maintain square shape after subdivision
			y_subdivisions=128,
			enter_editmode=False,
			location=(0, 0, self.water_level)
		)
		water = bpy.context.active_object
		water.name = name
		
		water.location = (0, 0, self.water_level)
		
		# Create water material
		mat = bpy.data.materials.new(name="WaterMaterial")
		mat.use_nodes = True
		nodes = mat.node_tree.nodes
		links = mat.node_tree.links
		
		# Clear default nodes
		nodes.clear()

		# Create shader nodes
		bsdf = nodes.new('ShaderNodeBsdfPrincipled')
		output = nodes.new('ShaderNodeOutputMaterial')
		
		# Configure water shader
		bsdf.inputs['Base Color'].default_value = (0.02, 0.15, 0.3, 1)  # Deep water color
		bsdf.inputs['Metallic'].default_value = 0.9
		bsdf.inputs['Roughness'].default_value = 0.1
		bsdf.inputs['Transmission Weight'].default_value = 0.95  # Changed key name
		bsdf.inputs['IOR'].default_value = 1.33  # Water's IOR

		bsdf.inputs['Subsurface Weight'].default_value = 0.8  # Enable subsurface
		bsdf.inputs['Subsurface Radius'].default_value = (0.5, 0.5, 0.5)  # Scattering distance

		# Add wave texture
		wave_tex = nodes.new('ShaderNodeTexWave')
		wave_tex.inputs['Scale'].default_value = 10.0
		wave_tex.inputs['Distortion'].default_value = 5.0
		
		# Mix with bump
		bump = nodes.new('ShaderNodeBump')
		bump.inputs['Strength'].default_value = 0.1
		links.new(wave_tex.outputs['Color'], bump.inputs['Height'])
		links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
		
		# Link nodes
		links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
		
		# Assign material
		water.data.materials.append(mat)

		# Add subdivision modifier
		subd = water.modifiers.new(name="Subdivision", type='SUBSURF')
		subd.levels = 2
		subd.render_levels = 3

		# Add edge split modifier to maintain hard boundaries
		edge_split = water.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
		edge_split.use_edge_angle = True
		edge_split.split_angle = math.radians(30)

		# Add displace modifier for waves
		displace = water.modifiers.new(name="WaveDisplace", type='DISPLACE')
		tex = bpy.data.textures.new("WaveTexture", type='CLOUDS')
		tex.noise_scale = 2.0
		displace.texture = tex
		displace.strength = 0.1

		# Ensure proper render settings
		water.cycles.use_adaptive_subdivision = True
		water.cycles.dicing_rate = 1.0
		
		return water

		# Usage:
		# create_water_plane(height=5.0)  # Creates water plane at Z=5