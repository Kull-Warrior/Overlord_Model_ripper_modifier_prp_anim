import struct
import math
import luaLib

class BinaryIO(object):
	def __init__(self, inputFile):
		self.inputFile=inputFile
		self.endian='<'
	
	def tell(self):
		"""Returns the current position of the read/write pointer within the input-file
		
		Function arguments:
		self 		--	Reference to the current instance of the class
		"""
		return self.inputFile.tell()

	def find(self,var,size=1000):
		""" Tries to find a given input within the input-file
		
		Function arguments:
		self 		--	Reference to the current instance of the class
		var			--	The to be searched input
		size		--	The block size in which the input is searched
		"""
		start=self.inputFile.tell()
		s=''
		while(True):
			data=self.inputFile.read(size)
			offset=data.find(var)
			if offset>=0:
				s+=data[:offset]
				self.inputFile.seek(start+offset+len(var))
				break
			else:
				s+=data
				start+=size
		return s

	def get_file_size(self):
		""" Gets the size of the input-file
		
		Function arguments:
		self 		--	Reference to the current instance of the class
		"""
		back=self.inputFile.tell()
		self.inputFile.seek(0,2)
		tell=self.inputFile.tell()
		self.inputFile.seek(back)
		return tell

	def seek(self,offset,from_where=0):
		""" Set the current position of the file pointer within a input-file
		
		Function arguments:
		self 		--	Reference to the current instance of the class
		offset		--	The number of bytes to move forward from the start of the input-file
		from_where	--	Defining the point of reference ( 0 beginning of the file, 1 current position of the file, 2 end of the file)
		"""
		self.inputFile.seek(offset,from_where)

	def half_to_float(h):
		s = int((h >> 15) & 0x00000001) # sign
		e = int((h >> 10) & 0x0000001f) # exponent
		f = int(h & 0x000003ff)   # fraction

		if e == 0:
			if f == 0:
				return int(s << 31)
			else:
				while not (f & 0x00000400):
					f <<= 1
					e -= 1
				e += 1
				f &= ~0x00000400
		elif e == 31:
			if f == 0:
				return int((s << 31) | 0x7f800000)
			else:
				return int((s << 31) | 0x7f800000 | (f << 13))

		e = e + (127 -15)
		f = f << 13
		return int((s << 31) | (e << 23) | f)

	def convert_half_to_float(h):
		id = half_to_float(h)
		str = struct.pack('I',id)
		return struct.unpack('f', str)[0]

	def find_all_occurrences(self, pattern):
		original_pos = self.tell()
		self.seek(0)
		occurrences = []
		pattern_len = len(pattern)
		chunk_size = 4096
		buffer = b''
		current_pos = 0

		while True:
			data = self.inputFile.read(chunk_size)
			if not data:
				break
			buffer += data
			while True:
				pos = buffer.find(pattern)
				if pos == -1:
					break
				occurrences.append(current_pos + pos)
				buffer = buffer[pos + pattern_len:]
				current_pos += pos + pattern_len
			if len(buffer) >= pattern_len - 1:
				keep = buffer[-(pattern_len - 1):]
				consumed = len(buffer) - len(keep)
				current_pos += consumed
				buffer = keep
			else:
				current_pos += len(buffer)
				buffer = b''
		self.seek(original_pos)
		return occurrences

	def find_offset(self, pattern):
		start_pos = self.tell()
		pattern_len = len(pattern)
		chunk_size = 4096
		buffer = b''
		while True:
			data = self.inputFile.read(chunk_size)
			if not data:
				break
			buffer += data
			pos = buffer.find(pattern)
			if pos != -1:
				found_offset = start_pos + pos
				self.seek(found_offset + pattern_len)
				return found_offset
			if len(buffer) >= pattern_len - 1:
				buffer = buffer[-(pattern_len - 1):]
				start_pos += len(data) - len(buffer)
			else:
				start_pos += len(data)
				buffer = b''
		return None

class BinaryReader(BinaryIO):
	"""general BinaryReader
	"""
	def __init__(self, inputFile):
		super(BinaryReader, self).__init__(inputFile)

	def read_from_data_type(self,length,format_characters,byte_count):
		data=struct.unpack(self.endian+length*format_characters,self.inputFile.read(length*byte_count))
		return data

	def read(self,count):
		return self.inputFile.read(count)

	def read_int8(self,length):
		return self.read_from_data_type(length,'b',1)

	def read_uint8(self,length):
		return self.read_from_data_type(length,'B',1)

	def read_short(self,length,format_characters='h',exp=12):
		array = []
		offset=self.inputFile.tell()
		for id in range(length):
			array.append(struct.unpack(self.endian+format_characters,self.inputFile.read(2))[0]*2**-exp)
		return array

	def read_int16(self,length):
		return self.read_from_data_type(length,'h',2)

	def read_uint16(self,length):
		return self.read_from_data_type(length,'H',2)

	def read_int32(self,length):
		return self.read_from_data_type(length,'i',4)

	def read_uint32(self,length):
		return self.read_from_data_type(length,'I',4)

	def read_int64(self,length):
		return self.read_from_data_type(length,'q',8)

	def read_uint64(self,length):
		return self.read_from_data_type(length,'Q',8)

	def read_float16(self,length,format_characters='h'):
		array = []
		offset=self.inputFile.tell()
		for id in range(length):
			array.append(convert_half_to_float(struct.unpack(self.endian+format_characters,self.inputFile.read(2))[0]))
		return array

	def read_float32(self,length):
		return self.read_from_data_type(length,'f',4)

	def read_double(self,length):
		return self.read_from_data_type(length,'d',8)

	def read_string(self, length):
		if length < 10000:
			offset = self.inputFile.tell()
			s = bytearray()
			for _ in range(length):
				lit = struct.unpack('c', self.inputFile.read(1))[0]
				if lit != b'\x00':
					s.extend(lit)
			return s.decode('utf-8')  # Decode bytes to a string

	def extract_byte_arrays(self, start_seq, end_seq):
		byte_arrays = []
		start_offsets = self.find_all_occurrences(start_seq)
		for start_offset in start_offsets:
			original_pos = self.tell()
			self.seek(start_offset)
			end_offset = self.find_offset(end_seq)
			if end_offset is not None:
				total_bytes = end_offset + len(end_seq) - start_offset
				self.seek(start_offset)
				data = self.read(total_bytes)
				#print(f"  Hex dump: {data.hex()[:156]}...")
				byte_arrays.append(data)
			self.seek(original_pos)
		return byte_arrays

	def get_map_data_offset(self, width, height):
		src_offset = 200 + width * height * 4
		total_number_of_bytes = 500
		
		# Read the relevant bytes from the file
		self.seek(src_offset)
		src = self.read(total_number_of_bytes)
		
		# The byte pattern to search for (b"IndoorSet")
		pattern = b'IndoorSet'
		
		max_first_char_slot = len(src) - len(pattern) + 1
		
		# Search through the byte array
		for i in range(max_first_char_slot):
			if src[i] != pattern[0]:
				continue
				
			# Check remaining bytes in reverse order for early exit
			matched = True
			for j in reversed(range(1, len(pattern))):  # Check from last byte to 2nd byte
				if src[i + j] != pattern[j]:
					matched = False
					break
					
			if matched:
				# Return the calculated offset (same logic as original C# code)
				return i + 200 - 4
		
		# Pattern not found
		return 0

	def read_map_data_from_file(self, offset, width, height):
		totalNumberOfBytes = width * height * 4
		self.seek(offset)
		data = self.read(totalNumberOfBytes)
		
		return data

	def get_map_water_level(self, input_file_name) -> float:
		"""Returns water level based on map file path patterns."""
		patterns = [
			("Exp - HalflingMain", 15),
			("Exp - Halfling Abyss", 50),
			("Exp - ElfMain", 15.3125),
			("Exp - Elf Abyss", 15),
			("Exp - PaladinMain", 15),
			("Exp - Paladin Abyss", 15),
			("Exp - DwarfMain", 50),
			("Exp - Dwarf Abyss", 0),
			("Exp - WarriorMain", 15),
			("Exp - Warrior Abyss - 01", 0),
			("Exp - Warrior Abyss - 02", 15.03125),
			("Exp - Tower_Dungeon", 15),
			("Exp - Tower_Spawnpit", 36.03125),
			("Exp - Tower", 0),
			("HalflingMain", 15),
			("SlaveCamp", 16.03125),
			("HalflingHomes1of2", 15),
			("HalflingHomes2of2", 15),
			("HellsKitchen", 20),
			("EntryCastleSpree", 15),
			("SpreeDungeon", 15),
			("ElfMain", 15),
			("GreenCave", 43),
			("SkullDen", 15.03125),
			("TrollTemple", 0),
			("PaladinMain", 15),
			("BlueCave", 25.03125),
			("Sewers1of2", 27.84375),
			("Sewers2of2", 18.03125),
			("Red Light Inn", 15),
			("Citadel", 15),
			("DwarfMain", 50),
			("GoldMine", 15),
			("Quarry", 40.71875),
			("HomeyHalls1of2", 0),
			("HomeyHalls2of2", 57.03125),
			("ArcaniumMine", 0),
			("RoyalHalls", 15),
			("WarriorMain", 15),
			("2P_Deathtrap", 0),
			("2P_Gates", 21),
			("2P_LastStand", 15.03125),
			("2P_PartyCrashers", 15.03125),
			("2P_Plunder", 15),
			("2P_TombRobber", 15),
			("Tower_Dungeon", 15),
			("Tower_Spawnpit", 36.03125),
			("Tower", 0),
			("PlayerMap", 15),
			("2P_Arena2", 0),
			("2P_Bombs", 15),
			("2P_GrabTheMaidens", 0),
			("2P_KillTheHoard", 0),
			("2P_KingoftheHill", 0),
			("2P_March_Mellow_Maidens", 0),
			("2P_Misty", 0),
			("2P_RockyRace", 0),
			("LM0A Netherworld", 0),
			("LM0C Netherworld Burrows", 0),
			("LM0D Netherworld Foundations", 0),
			("Exp - LM0B Netherworld Arena", 0),
			("LM1A Hunting Grounds", 15),
			("LM1C Nordberg Town", 22),
			("LM1D Nordberg Fairyland", 18),
			("LM1E Nordhaven", 22),
			("LM1F Prelude", 22),
			("LM1G Nordberg Commune", 30),
			("LM2A Everlight Gates", 25.25),
			("LM2B Everlight Jungle A", 74),
			("LM2C Everlight Facility", 71),
			("LM2D Everlight Jungle B", 70),
			("LM2E Spider Boss", 48.0625),
			("LM2F Everlight Town", 26.5),
			("LM3A Wasteland", 0),
			("LM3B Wasteland Sanctuary Depths", 16),
			("LM3C Wasteland Sanctuary Town", 0),
			("LM4A Empire Heartland Harbour", 20),
			("LM4B Empire Heartland City", 36.5),
			("LM4C Empire Heartland Assault", 15),
			("LM4D Empire City", 15),
			("LM4E Empire Sewers", 41),
			("LM4F Empire Arena", 40),
			("LM4G Empire Palace", 16),
			("LM4H Empire EndBoss", 15),
			("MPC1_Arena", 53),
			("MPC2_Invasion", 16),
			("MPV1_Dominate", 15),
			("MPV2_PiratePlunder", 25.3125)
		]

		for pattern, value in patterns:
			if pattern in input_file_name:
				return value
		return 0.0

class BinaryWriter(BinaryIO):
	def __init__(self, inputFile):
		super(BinaryWriter, self).__init__(inputFile)

	def write_as_data_type(self,data_to_write,format_characters):
		for m in range(len(data_to_write)):
			data=struct.pack(self.endian+format_characters,data_to_write[m])
			self.inputFile.write(data)

	def write_int8(self,data):
		self.write_as_data_type(data,'b')

	def write_uint8(self,data):
		self.write_as_data_type(data,'B')

	def write_int16(self,data):
		self.write_as_data_type(data,'h')

	def write_uint16(self,data):
		self.write_as_data_type(data,'H')

	def write_int32(self,data):
		self.write_as_data_type(data,'i')

	def write_uint32(self,data):
		self.write_as_data_type(data,'I')

	def write_int64(self,data):
		self.write_as_data_type(data,'q')

	def write_uint64(self,data):
		self.write_as_data_type(data,'Q')

	def write_float32(self,data):
		self.write_as_data_type(data,'f')

	def write_double(self,data):
		self.write_as_data_type(data,'d')

	def write_string(self,string):
		self.inputFile.write(string)

	def write_to_dxt_file(self,image):
		#Write DDS header
		##Write Magic number / file identifier
		self.write_string(b'\x44\x44\x53\x20')
		##Write Header Size
		self.write_string(b'\x7C\x00\x00\x00')
		##Write Flags
		self.write_string(b'\x07\x10\x02\x00')
		##Write image height
		self.write_string(struct.pack('i',image.height))
		##Write image width
		self.write_string(struct.pack('i',image.width))
		##Write PitchOrLinearSize
		self.write_string(b'\x00\x00\x00\x00')
		##Write Depth
		self.write_string(b'\x00\x00\x00\x00')
		##Write MipMapCount
		mipmap_count=math.floor(math.log(max(image.width,image.height),2))+1
		self.write_string(struct.pack('i',mipmap_count))
		##Write Reserved 11 x 4 Bytes
		self.write_string(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		##Write DDPIXELFORMAT
		###Write Header Size
		self.write_string(b'\x20\x00\x00\x00')
		###Write Flags
		self.write_string(b'\x04\x00\x00\x00')
		###Write FourCC
		self.write_string(image.format.encode('utf-8'))
		###Write RGBBitCount
		self.write_string(b'\x00\x00\x00\x00')
		###Write RBitMask
		self.write_string(b'\x00\x00\x00\x00')
		###Write GBitMask
		self.write_string(b'\x00\x00\x00\x00')
		###Write BBitMask
		self.write_string(b'\x00\x00\x00\x00')
		###Write RGBAlphaBitMask
		self.write_string(b'\x00\x00\x00\x00')
		###Write Caps
		self.write_string(b'\x08\x10\x40\x00')
		###Write Caps2
		self.write_string(b'\x00\x00\x00\x00')
		###Write Caps3
		self.write_string(b'\x00\x00\x00\x00')
		###Write Caps4
		self.write_string(b'\x00\x00\x00\x00')
		##Write Reserved2
		self.write_string(b'\x00\x00\x00\x00')
		##Write data
		self.write_string(image.data)

	def write_to_tga_file(self,image,offset,data):
		#Write tga header
		self.write_string(b'\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		#Write image height
		self.write_string(struct.pack('H',image.height))
		#Write image width
		self.write_string(struct.pack('H',image.width))
		#Write data offset
		self.write_string(offset)
		#Write data
		self.write_string(data)