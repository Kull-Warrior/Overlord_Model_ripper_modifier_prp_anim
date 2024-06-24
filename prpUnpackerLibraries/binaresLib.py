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

def unknown_reading_functionality_needs_to_be_renamed(self,n,first_multiplier,second_multiplier,third_multiplier,first_read_value,second_read_value):
	offset=self.inputFile.tell()
	if self.xor_key is None:
		data=struct.unpack(self.endian+n*first_multiplier,self.inputFile.read(first_read_value))
	else:
		data=struct.unpack(self.endian+n*second_multiplier,self.inputFile.read(second_read_value))
		self.xor(data)
		data=struct.unpack(self.endian+n*third_multiplier,self.xor_data)
	return data

def unknown_writing_functionality_needs_to_be_renamed(self,n,adder):
	for m in range(len(n)):
		data=struct.pack(self.endian+adder,n[m])
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

	def int64(self,n):
		if self.inputFile.mode=='rb':
			return unknown_reading_functionality_needs_to_be_renamed(self,n,'q',8*'B','q',n*8,n*8)
		if self.inputFile.mode=='wb':
			unknown_writing_functionality_needs_to_be_renamed(self,n,'q')

	def uint64(self,n):
		if self.inputFile.mode=='rb':
			return unknown_reading_functionality_needs_to_be_renamed(self,n,'Q',8*'B','Q',n*8,n*8)
		if self.inputFile.mode=='wb':
			unknown_writing_functionality_needs_to_be_renamed(self,n,'Q')

	def int32(self,n):
		if self.inputFile.mode=='rb':
			return unknown_reading_functionality_needs_to_be_renamed(self,n,'i',4*'B','i',n*4,n*4)
		if self.inputFile.mode=='wb':
			unknown_writing_functionality_needs_to_be_renamed(self,n,'i')

	def uint32(self,n):
		if self.inputFile.mode=='rb':
			return unknown_reading_functionality_needs_to_be_renamed(self,n,'I',4*'B','I',n*4,n*4)
		if self.inputFile.mode=='wb':
			unknown_writing_functionality_needs_to_be_renamed(self,n,'I')

	def uint8(self,n):
		if self.inputFile.mode=='rb':
			return unknown_reading_functionality_needs_to_be_renamed(self,n,'B','B','B',n,n)
		if self.inputFile.mode=='wb':
			unknown_writing_functionality_needs_to_be_renamed(self,n,'B')

	def int8(self,n):
		if self.inputFile.mode=='rb':
			return unknown_reading_functionality_needs_to_be_renamed(self,n,'b','b','b',n,n)
		if self.inputFile.mode=='wb':
			unknown_writing_functionality_needs_to_be_renamed(self,n,'b')

	def int16(self,n):
		if self.inputFile.mode=='rb':
			return unknown_reading_functionality_needs_to_be_renamed(self,n,'h',2*'B','h',n*2,n*2)
		if self.inputFile.mode=='wb':
			unknown_writing_functionality_needs_to_be_renamed(self,n,'h')

	def uint16(self,n):
		if self.inputFile.mode=='rb':
			return unknown_reading_functionality_needs_to_be_renamed(self,n,'H',2*'B','H',n*2,n*2)
		if self.inputFile.mode=='wb':
			unknown_writing_functionality_needs_to_be_renamed(self,n,'H')

	def float(self,n):
		if self.inputFile.mode=='rb':
			return unknown_reading_functionality_needs_to_be_renamed(self,n,'f',4*'B','f',n*4,n*4)
		if self.inputFile.mode=='wb':
			unknown_writing_functionality_needs_to_be_renamed(self,n,'f')

	def double(self,n):
		if self.inputFile.mode=='rb':
			return unknown_reading_functionality_needs_to_be_renamed(self,n,'d',8*'B','d',n*8,n*8)
		if self.inputFile.mode=='wb':
			unknown_writing_functionality_needs_to_be_renamed(self,n,'d')

	def half(self,n,h='h'):
		array = []
		offset=self.inputFile.tell()
		for id in range(n):
			array.append(convert_half_to_float(struct.unpack(self.endian+h,self.inputFile.read(2))[0]))
		return array

	def short(self,n,h='h',exp=12):
		array = []
		offset=self.inputFile.tell()
		for id in range(n):
			array.append(struct.unpack(self.endian+h,self.inputFile.read(2))[0]*2**-exp)
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