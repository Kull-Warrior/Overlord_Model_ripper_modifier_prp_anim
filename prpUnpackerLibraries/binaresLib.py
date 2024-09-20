import struct

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

def read_from_data_type(self,length,format_characters,xor_format_characters,byte_count):
	offset=self.inputFile.tell()
	if self.xor_key is None:
		data=struct.unpack(self.endian+length*format_characters,self.inputFile.read(length*byte_count))
	else:
		data=struct.unpack(self.endian+length*byte_count*xor_format_characters,self.inputFile.read(length*byte_count))
		self.xor(data)
		data=struct.unpack(self.endian+length*format_characters,self.xor_data)
	return data

def write_as_data_type(self,data_to_write,format_characters):
	for m in range(len(data_to_write)):
		data=struct.pack(self.endian+format_characters,data_to_write[m])
		self.inputFile.write(data)

class BinaryReader(file):
	"""general BinaryReader
	"""
	def __init__(self, inputFile):
		self.inputFile=inputFile
		self.endian='<'
		self.stream={}
		self.xor_key=None
		self.xor_offset=0
		self.xor_data=''

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
		return read_from_data_type(self,length,'q','B',8)

	def write_int64(self,data):
		write_as_data_type(self,data,'q')
	
	def read_uint64(self,length):
		return read_from_data_type(self,length,'Q','B',8)

	def write_uint64(self,data):
		write_as_data_type(self,data,'Q')
	
	def read_int32(self,length):
		return read_from_data_type(self,length,'i','B',4)

	def write_int32(self,data):
		write_as_data_type(self,data,'i')
	
	def read_uint32(self,length):
		return read_from_data_type(self,length,'I','B',4)

	def write_uint32(self,data):
		write_as_data_type(self,data,'I')
	
	def read_uint8(self,length):
		return read_from_data_type(self,length,'B','B',1)

	def write_uint8(self,data):
		write_as_data_type(self,data,'B')

	def read_int8(self,length):
		return read_from_data_type(self,length,'b','b',1)

	def write_int8(self,data):
		write_as_data_type(self,data,'b')
	
	def read_int16(self,length):
		return read_from_data_type(self,length,'h','B',2)
	
	def write_int16(self,data):
		write_as_data_type(self,data,'h')

	def read_uint16(self,length):
		return read_from_data_type(self,length,'H','B',2)

	def write_uint16(self,data):
		write_as_data_type(self,data,'H')

	def read_float(self,length):
		return read_from_data_type(self,length,'f','B',4)
	
	def write_float(self,data):
		write_as_data_type(self,data,'f')

	def read_double(self,length):
		return read_from_data_type(self,length,'d','B',8)

	def write_double(self,data):
		write_as_data_type(self,data,'d')

	def half(self,length,format_characters='h'):
		array = []
		offset=self.inputFile.tell()
		for id in range(length):
			array.append(convert_half_to_float(struct.unpack(self.endian+format_characters,self.inputFile.read(2))[0]))
		return array

	def short(self,length,format_characters='h',exp=12):
		array = []
		offset=self.inputFile.tell()
		for id in range(length):
			array.append(struct.unpack(self.endian+format_characters,self.inputFile.read(2))[0]*2**-exp)
		return array

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

	def read(self,count):
		back=self.inputFile.tell()
		if self.xor_key is None:
			return self.inputFile.read(count)
		else:
			data=struct.unpack(self.endian+n*'B',self.inputFile.read(n))
			self.xor(data)
			return self.xor_data

	def tell(self):
		"""Returns the current position of the read/write pointer within the input-file
		
		Function arguments:
		self 		--	Reference to the current instance of the class
		"""
		return self.inputFile.tell()

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

	def write_word(self,word):
		if word<10000:
			self.inputFile.write(word)

	def stream(self,stream_name,element_count,element_size):
		self.inputFile.seek(element_count*element_size,1)
		self.stream[stream_name]['offset']=offset
		self.stream[stream_name]['element_count']=element_count
		self.stream[stream_name]['element_size']=element_size