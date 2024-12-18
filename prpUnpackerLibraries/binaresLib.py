import struct
import math

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

	def read_string(self,length):
		if length<10000:
			offset=self.inputFile.tell()
			s=''
			for j in range(0,length):
				lit =  struct.unpack('c',self.inputFile.read(1))[0]

				if ord(lit)!=0:
					s+=lit
			return s

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
		self.write_string('\x44\x44\x53\x20')
		##Write Header Size
		self.write_string('\x7C\x00\x00\x00')
		##Write Flags
		self.write_string('\x07\x10\x02\x00')
		##Write image height
		self.write_string(struct.pack('i',image.height))
		##Write image width
		self.write_string(struct.pack('i',image.width))
		##Write PitchOrLinearSize
		self.write_string('\x00\x00\x00\x00')
		##Write Depth
		self.write_string('\x00\x00\x00\x00')
		##Write MipMapCount
		mipmap_count=math.floor(math.log(max(image.width,image.height),2))+1
		self.write_string(struct.pack('i',mipmap_count))
		##Write Reserved 11 x 4 Bytes
		self.write_string('\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		##Write DDPIXELFORMAT
		###Write Header Size
		self.write_string('\x20\x00\x00\x00')
		###Write Flags
		self.write_string('\x04\x00\x00\x00')
		###Write FourCC
		self.write_string(image.format)
		###Write RGBBitCount
		self.write_string('\x00\x00\x00\x00')
		###Write RBitMask
		self.write_string('\x00\x00\x00\x00')
		###Write GBitMask
		self.write_string('\x00\x00\x00\x00')
		###Write BBitMask
		self.write_string('\x00\x00\x00\x00')
		###Write RGBAlphaBitMask
		self.write_string('\x00\x00\x00\x00')
		###Write Caps
		self.write_string('\x08\x10\x40\x00')
		###Write Caps2
		self.write_string('\x00\x00\x00\x00')
		###Write Caps3
		self.write_string('\x00\x00\x00\x00')
		###Write Caps4
		self.write_string('\x00\x00\x00\x00')
		##Write Reserved2
		self.write_string('\x00\x00\x00\x00')
		##Write data
		self.write_string(image.data)

	def write_to_tga_file(self,image,offset,data):
		#Write tga header
		self.write_string('\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		#Write image height
		self.write_string(struct.pack('H',image.height))
		#Write image width
		self.write_string(struct.pack('H',image.width))
		#Write data offset
		self.write_string(offset)
		#Write data
		self.write_string(data)