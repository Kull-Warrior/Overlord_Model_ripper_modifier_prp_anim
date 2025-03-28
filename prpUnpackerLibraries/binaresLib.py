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