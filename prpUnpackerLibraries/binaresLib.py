import struct
import Blender

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
			#print s,e,f
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

	def q(self,n):
		offset=self.inputFile.tell()
		data=struct.unpack(self.endian+n*'q',self.inputFile.read(n*8))
		return data

	def i(self,n):
		if self.inputFile.mode=='rb':
			offset=self.inputFile.tell()
			if self.xor_key is None:
				data=struct.unpack(self.endian+n*'i',self.inputFile.read(n*4))
			else:
				data=struct.unpack(self.endian+n*4*'B',self.inputFile.read(n*4))
				self.xor(data)
				data=struct.unpack(self.endian+n*'i',self.xor_data)
			return data
		if self.inputFile.mode=='wb':
			for m in range(len(n)):
				data=struct.pack(self.endian+'i',n[m])
				self.inputFile.write(data)

	def I(self,n):
		offset=self.inputFile.tell()
		if self.xor_key is None:
			data=struct.unpack(self.endian+n*'I',self.inputFile.read(n*4))
		else:
			data=struct.unpack(self.endian+n*4*'B',self.inputFile.read(n*4))
			self.xor(data)
			data=struct.unpack(self.endian+n*'I',self.xor_data)
		return data

	def B(self,n):
		if self.inputFile.mode=='rb':
			offset=self.inputFile.tell()
			if self.xor_key is None:
				data=struct.unpack(self.endian+n*'B',self.inputFile.read(n))
			else:
				data=struct.unpack(self.endian+n*'B',self.inputFile.read(n))
				self.xor(data)
				data=struct.unpack(self.endian+n*'B',self.xor_data)
			return data
		if self.inputFile.mode=='wb':
			for m in range(len(n)):
				data=struct.pack(self.endian+'B',n[m])
				self.inputFile.write(data)

	def b(self,n):
		if self.inputFile.mode=='rb':
			offset=self.inputFile.tell()
			if self.xor_key is None:
				data=struct.unpack(self.endian+n*'b',self.inputFile.read(n))
			else:
				data=struct.unpack(self.endian+n*'b',self.inputFile.read(n))
				self.xor(data)
				data=struct.unpack(self.endian+n*'b',self.xor_data)
			return data
		if self.inputFile.mode=='wb':
			for m in range(len(n)):
				data=struct.pack(self.endian+'b',n[m])
				self.inputFile.write(data)

	def h(self,n):
		if self.inputFile.mode=='rb':
			offset=self.inputFile.tell()
			if self.xor_key is None:
				data=struct.unpack(self.endian+n*'h',self.inputFile.read(n*2))
			else:
				data=struct.unpack(self.endian+n*2*'B',self.inputFile.read(n*2))
				self.xor(data)
				data=struct.unpack(self.endian+n*'h',self.xor_data)
			return data
		if self.inputFile.mode=='wb':
			for m in range(len(n)):
				data=struct.pack(self.endian+'h',n[m])
				self.inputFile.write(data)

	def H(self,n):
		if self.inputFile.mode=='rb':
			offset=self.inputFile.tell()
			if self.xor_key is None:
				data=struct.unpack(self.endian+n*'H',self.inputFile.read(n*2))
			else:
				data=struct.unpack(self.endian+n*2*'B',self.inputFile.read(n*2))
				self.xor(data)
				data=struct.unpack(self.endian+n*'H',self.xor_data)
			return data
		if self.inputFile.mode=='wb':
			for m in range(len(n)):
				data=struct.pack(self.endian+'H',n[m])
				self.inputFile.write(data)

	def f(self,n):
		if self.inputFile.mode=='rb':
			offset=self.inputFile.tell()
			if self.xor_key is None:
				data=struct.unpack(self.endian+n*'f',self.inputFile.read(n*4))
			else:
				data=struct.unpack(self.endian+n*4*'B',self.inputFile.read(n*4))
				self.xor(data)
				data=struct.unpack(self.endian+n*'f',self.xor_data)
			return data
		if self.inputFile.mode=='wb':
			for m in range(len(n)):
				data=struct.pack(self.endian+'f',n[m])
				self.inputFile.write(data)

	def half(self,n,h='h'):
		array = []
		offset=self.inputFile.tell()
		for id in range(n):
			#array.append(convert_half_to_float(struct.unpack(self.endian+'H',self.inputFile.read(2))[0]))
			array.append(convert_half_to_float(struct.unpack(self.endian+h,self.inputFile.read(2))[0]))
		return array

	def short(self,n,h='h',exp=12):
		array = []
		offset=self.inputFile.tell()
		for id in range(n):
			array.append(struct.unpack(self.endian+h,self.inputFile.read(2))[0]*2**-exp)
			#array.append(self.H(1)[0]*2**-exp)
		return array

	def i12(self,n):
		array = []
		offset=self.inputFile.tell()
		for id in range(n):
			if self.endian=='>':
				var='\x00'+self.inputFile.read(3)
			if self.endian=='<':
				var=self.inputFile.read(3)+'\x00'
			array.append(struct.unpack(self.endian+'i',var)[0])
		return array

	def find(self,var,size=1000):
		start=self.inputFile.tell()
		s=''
		while(True):
			data=self.inputFile.read(size)
			offset=data.find(var)
			#print offset
			if offset>=0:
				s+=data[:offset]
				self.inputFile.seek(start+offset+len(var))
				#print 'znaleziono',var,'offset=',self.inputFile.tell()
				break
			else:
				s+=data
				start+=size
		return s

	def find_all(self,var,size=100):
		list=[]
		start=self.inputFile.tell()
		while(True):
			data=self.inputFile.read(size)
			offset=data.find(var)
			#print offset,self.inputFile.tell()
			if offset>=0:
				list.append(start+offset)
				self.inputFile.seek(start+offset+len(var))
				if self.debug==True:
					print start+offset
			else:
				start+=size
				self.inputFile.seek(start)
			if self.inputFile.tell()>self.file_size():
				break
		return list

	def find_char(self,var):
		offset=self.inputFile.find(var)
		return offset

	def file_size(self):
		back=self.inputFile.tell()
		self.inputFile.seek(0,2)
		tell=self.inputFile.tell()
		#self.inputFile.seek(0)
		self.inputFile.seek(back)
		return tell

	def seek(self,offset,a=0):
		self.inputFile.seek(offset,a)

	def seekpad(self,pad,type=0):
		''' 16-byte chunk alignment'''
		size=self.inputFile.tell()
		seek = (pad - (size % pad)) % pad
		if type==1:
			if seek==0:
				seek+=pad
		self.inputFile.seek(seek, 1)

	def read(self,count):
		back=self.inputFile.tell()
		if self.xor_key is None:
			return self.inputFile.read(count)
		else:
			data=struct.unpack(self.endian+n*'B',self.inputFile.read(n))
			self.xor(data)
			return self.xor_data

	def tell(self):
		val=self.inputFile.tell()
		return val

	def word(self,long):
		if long<10000:
			if self.inputFile.mode=='rb':
				offset=self.inputFile.tell()
				s=''
				for j in range(0,long):
					if self.xor_key is None:
						lit =  struct.unpack('c',self.inputFile.read(1))[0]
						#data=struct.unpack(self.endian+n*'i',self.inputFile.read(n*4))
					else:
						data=struct.unpack(self.endian+'B',self.inputFile.read(1))
						self.xor(data)
						lit=struct.unpack(self.endian+'c',self.xor_data)[0]
						#lit =  struct.unpack('c',self.inputFile.read(1))[0]
					if ord(lit)!=0:
						s+=lit
				return s
			if self.inputFile.mode=='wb':
				#data=self.inputFile.read(long)
				self.inputFile.write(long)
			#return 0

	def stream(self,stream_name,element_count,element_size):
		self.inputFile.seek(element_count*element_size,1)
		self.stream[stream_name]['offset']=offset
		self.stream[stream_name]['element_count']=element_count
		self.stream[stream_name]['element_size']=element_size