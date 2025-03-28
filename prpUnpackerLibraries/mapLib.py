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

	def create_full_terrain_scene(self, name="Terrain", scale=1.0, vertical_scale=1.0, center_mesh=True):
		"""Instance method that uses the class' own height data"""
		# Get height data from the class instance
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
		mesh.update()
		
		# Center mesh if requested
		if center_mesh:
			obj.location = (-256 * scale, -256 * scale, 0)

		# Add to scene
		bpy.context.collection.objects.link(obj)
		bpy.context.view_layer.objects.active = obj
		obj.select_set(True)

		# Create material
		mat = bpy.data.materials.new(name="TerrainMaterial")
		mat.use_nodes = True
		nodes = mat.node_tree.nodes
		nodes.clear()
		
		# Create basic principled BSDF material
		bsdf = nodes.new('ShaderNodeBsdfPrincipled')
		bsdf.inputs['Base Color'].default_value = (0.3, 0.9, 0.2, 1)  # Green color
		output = nodes.new('ShaderNodeOutputMaterial')
		mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
		obj.data.materials.append(mat)

		# Calculate normals
		mesh.calc_normals()

		# Create lighting
		bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 0, 100))
		sun = bpy.context.active_object
		sun.data.energy = 5.0

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

		# Frame the object in the viewport
		bpy.ops.view3d.view_selected()

		return obj

		# Usage example:
		# create_full_terrain_scene(height_data, scale=0.5, vertical_scale=2.0)