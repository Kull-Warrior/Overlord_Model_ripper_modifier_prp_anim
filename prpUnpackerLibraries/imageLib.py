import struct
import Blender

def get_dds_header():
	dds_header = '\x44\x44\x53\x20\x7C\x00\x00\x00\x07\x10\x0A\x00\x00\x04\x00\x00\x00\x04\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x0B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x05\x00\x00\x00\x44\x58\x54\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x10\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	return dds_header

def get_tga_header():
	tga_header = '\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	return tga_header

def write_to_dxt_file(self):
	newfile=open(self.name,'wb')
	newfile.write(get_dds_header())
	newfile.seek(0xC)
	newfile.write(struct.pack('i',self.height))
	newfile.seek(0x10)
	newfile.write(struct.pack('i',self.width))
	newfile.seek(0x54)
	newfile.write(self.format)
	newfile.seek(128)
	newfile.write(self.data)
	newfile.close()

def write_to_tga_file(self,offset,data):
	newfile=open(self.name,'wb')
	newfile.write(get_tga_header())
	newfile.write(struct.pack('H',self.height))
	newfile.write(struct.pack('H',self.width))
	newfile.write(offset)
	newfile.write(data)
	newfile.close()

def tga_16(data):
	newdata=''
	for m in range(len(data)/2):
		a=struct.unpack('H',data[m*2:m*2+2])[0]
		red = (a & 0xF800) >11
		green = (a & 0x07E0) >5
		blue = (a & 0x001F)
		red = red * 255 / 31
		green = green * 255 / 63
		blue = blue * 255 / 31
		newdata+=struct.pack('iii',red,green,blue)
	return newdata

def rgb565_to_rgb888(width,height,data,outname):
	newdata=''
	start=0
	image=Blender.Image.New(outname,width,height,24)
	for m in range(width):
		for n in range(height):
			c=struct.unpack('H',data[start:start+2])[0]
			start+=2
			red = (c>>11)&0x1f
			green = (c>>5)&0x3f
			blue = c&0x001f
			pred=(red<<3)|(red>>2)
			pgreen=(green<<2)|(green>>4)
			pblue=(blue<<3)|(blue>>2)
			if pr==0 and pg==0 and pb==0:
				palpha=1
			else:
				palpha=0
			image.setPixelI(n, 511-m, (pred, pgreen, pblue,palpha))
	image.save()

class Image():
	def __init__(self):
		self.format=None
		self.height=None
		self.width=None
		self.name=None
		self.data=None

	def draw(self):
		if None not in (self.format, self.height, self.width, self.name,self.data):
			if 'DXT' in self.format:
				write_to_dxt_file(self)
			elif 'tga' in self.format:
				if self.format=='tga32':
					offset='\x20\x20'
					data=self.data
				elif self.format=='tga16':
					offset='\x20\x20'
					data=tga_16(self.data)
				elif self.format=='tga24':
					offset='\x18\x20'
					data=self.data
				write_to_tga_file(self,offset,data)
			elif self.format=='565to888':
				rgb565_to_rgb888(self.width,self.height,self.data,self.name)
			else:
				print 'Warning: unknown image format',self.format