import Blender,os
import zlib

def inflate(data):
	decompress = zlib.decompressobj(
			-zlib.MAX_WBITS  # see above
	)
	inflated = decompress.decompress(data)
	inflated += decompress.flush()
	return inflated

class Unpacker:
	"""
	'Unpacker'
	self.file_count=None
	self.name_list=[]
	self.offsetlist=[]
	self.size_list=[]
	self.filecomtypelist=[]
	self.zlib=True
	self.output_directory=''
	self.input_file=None
	"""
	def __init__(self):
		self.file_count=None
		self.name_list=[]
		self.offset_list=[]
		self.size_list=[]
		self.data_list=[]
		self.compTypeList=[]
		self.zlib=False
		self.inflate=False
		self.output_directory=None
		self.input_file=None

	def unpack(self):
		if self.zlib==True:
			import zlib
		if self.input_file is not None:
			archive=open(self.input_file,'rb')
			if self.output_directory is not None:
				if self.file_count==len(self.data_list):
					for m in range(self.file_count):
						newfiledir=self.output_directory+os.sep+Blender.sys.dirname(self.name_list[m])
						try:os.makedirs(newfiledir)
						except:pass
						newfile=open(self.output_directory+os.sep+self.name_list[m],'wb')
						data=self.data_list[m]
						newfile.write(data)
						print self.name_list[m]
						newfile.close()

				if len(self.offset_list)==len(self.size_list)==len(self.name_list):
					self.file_count=len(self.name_list)
					for m in range(self.file_count):
						archive.seek(self.offset_list[m],0)
						newfiledir=self.output_directory+os.sep+Blender.sys.dirname(self.name_list[m])
						try:os.makedirs(newfiledir)
						except:pass
						newfile=open(self.output_directory+os.sep+self.name_list[m],'wb')
						if self.zlib==True:
							try:
								data=zlib.decompress(archive.read(self.size_list[m]))
								newfile.write(data)
								print 'unpackING...',self.name_list[m]
							except:
								print 'zlib warning.NOT unpackED',self.name_list[m]
						elif self.inflate==True:
							data=inflate(archive.read(self.size_list[m]))
							newfile.write(data)
						else:
							data=archive.read(self.size_list[m])
							newfile.write(data)
						print self.name_list[m]
						newfile.close()
				else:
					print 'MISSING....'
			else:
				print 'NO output_directory DIR'
			archive.close()
		else:
			print 'NO ARCHIVE'