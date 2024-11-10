import struct

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
		self.xor_key=None
		self.xor_offset=0
		self.xor_data=''

	def read_from_data_type(self,length,format_characters,xor_format_characters,byte_count):
		offset=self.inputFile.tell()
		if self.xor_key is None:
			data=struct.unpack(self.endian+length*format_characters,self.inputFile.read(length*byte_count))
		else:
			data=struct.unpack(self.endian+length*byte_count*xor_format_characters,self.inputFile.read(length*byte_count))
			self.xor(data)
			data=struct.unpack(self.endian+length*format_characters,self.xor_data)
		return data

	def xor(self,data):
			self.xor_data=''
			for m in range(len(data)):
				ch=ord(chr(data[m] ^ self.xor_key[self.xor_offset]))
				self.xor_data+=struct.pack('B',ch)
				if self.xor_offset==len(self.xor_key)-1:
					self.xor_offset=0
				else:
					self.xor_offset+=1

	def read_int64(self,length):
		return self.read_from_data_type(length,'q','B',8)
	
	def read_uint64(self,length):
		return self.read_from_data_type(length,'Q','B',8)
	
	def read_int32(self,length):
		return self.read_from_data_type(length,'i','B',4)
	
	def read_uint32(self,length):
		return self.read_from_data_type(length,'I','B',4)
	
	def read_uint8(self,length):
		return self.read_from_data_type(length,'B','B',1)

	def read_int8(self,length):
		return self.read_from_data_type(length,'b','b',1)
	
	def read_int16(self,length):
		return self.read_from_data_type(length,'h','B',2)

	def read_uint16(self,length):
		return self.read_from_data_type(length,'H','B',2)

	def read_float(self,length):
		return self.read_from_data_type(length,'f','B',4)

	def read_double(self,length):
		return self.read_from_data_type(length,'d','B',8)

	def read_half(self,length,format_characters='h'):
		array = []
		offset=self.inputFile.tell()
		for id in range(length):
			array.append(convert_half_to_float(struct.unpack(self.endian+format_characters,self.inputFile.read(2))[0]))
		return array

	def read_short(self,length,format_characters='h',exp=12):
		array = []
		offset=self.inputFile.tell()
		for id in range(length):
			array.append(struct.unpack(self.endian+format_characters,self.inputFile.read(2))[0]*2**-exp)
		return array

	def read(self,count):
		back=self.inputFile.tell()
		if self.xor_key is None:
			return self.inputFile.read(count)
		else:
			data=struct.unpack(self.endian+n*'B',self.inputFile.read(n))
			self.xor(data)
			return self.xor_data

	def read_word(self,length):
		if length<10000:
			offset=self.inputFile.tell()
			s=''
			for j in range(0,length):
				if self.xor_key is None:
					lit =  struct.unpack('c',self.inputFile.read(1))[0]
				else:
					data=struct.unpack(self.endian+'B',self.inputFile.read(1))
					self.xor(data)
					lit=struct.unpack(self.endian+'c',self.xor_data)[0]
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

	def write_int64(self,data):
		self.write_as_data_type(data,'q')

	def write_uint64(self,data):
		self.write_as_data_type(data,'Q')

	def write_int32(self,data):
		self.write_as_data_type(data,'i')

	def write_uint32(self,data):
		self.write_as_data_type(data,'I')

	def write_int16(self,data):
		self.write_as_data_type(data,'h')

	def write_uint16(self,data):
		self.write_as_data_type(data,'H')

	def write_int8(self,data):
		self.write_as_data_type(data,'b')

	def write_uint8(self,data):
		self.write_as_data_type(data,'B')

	def write_float(self,data):
		self.write_as_data_type(data,'f')

	def write_double(self,data):
		self.write_as_data_type(data,'d')

	def write_word(self,word):
		self.inputFile.write(word)

	def write_to_dxt_file(self,image):
		#Write DDS header
		self.write_word('\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x00\x04\x00\x00\x00\x04\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x0B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x05\x00\x00\x00\x44\x58\x54\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		self.seek(0xC)
		#Write image height
		self.write_word(struct.pack('i',image.height))
		self.seek(0x10)
		#Write image width
		self.write_word(struct.pack('i',image.width))
		self.seek(0x54)
		#Write image format
		self.write_word(image.format)
		self.seek(128)
		#Write data
		self.write_word(image.data)

	def write_to_tga_file(self,image,offset,data):
		#Write tga header
		self.write_word('\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00')
		#Write image height
		self.write_word(struct.pack('H',image.height))
		#Write image width
		self.write_word(struct.pack('H',image.width))
		#Write data offset
		self.write_word(offset)
		#Write data
		self.write_word(data)