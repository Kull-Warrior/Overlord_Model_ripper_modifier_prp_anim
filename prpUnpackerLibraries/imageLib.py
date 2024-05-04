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
	newfile.write(struct.pack('i',self.wys))
	newfile.seek(0x10)
	newfile.write(struct.pack('i',self.szer))
	newfile.seek(0x54)
	newfile.write(self.format)
	newfile.seek(128)
	newfile.write(self.data)
	newfile.close()

def write_to_tga_file(self,offset,data):
	newfile=open(self.name,'wb')
	newfile.write(get_tga_header())
	newfile.write(struct.pack('H',self.wys))
	newfile.write(struct.pack('H',self.szer))
	newfile.write(offset)
	newfile.write(data)
	newfile.close()

def tga_16(data):
	newdata=''
	for m in range(len(data)/2):
		a=struct.unpack('H',data[m*2:m*2+2])[0]
		r = (a & 0xF800) >11
		g = (a & 0x07E0) >5
		b = (a & 0x001F)
		r = r * 255 / 31
		g = g * 255 / 63
		b = b * 255 / 31
		newdata+=struct.pack('iii',r,g,b)
	return newdata

def rgb565_to_rgb888(szer,wys,data,outname):
	newdata=''
	start=0
	image=Blender.Image.New(outname,szer,wys,24)
	for m in range(szer):
		for n in range(wys):
			c=struct.unpack('H',data[start:start+2])[0]
			start+=2
			r = (c>>11)&0x1f
			g = (c>>5)&0x3f
			b = c&0x001f
			pr=(r<<3)|(r>>2)
			pg=(g<<2)|(g>>4)
			pb=(b<<3)|(b>>2)
			if pr==0 and pg==0 and pb==0:
				pa=1
			else:
				pa=0
			image.setPixelI(n, 511-m, (pr, pg, pb,pa))
	image.save()

def argb1555_to_argb8888(data):
	newdata=''
	for m in range(len(data)/2):
		c=struct.unpack('H',data[m*2:m*2+2])[0]
		a = c&0x8000
		r = c&0x7C00
		g = c&0x03E0
		b = c&0x1F
		rgb = (r << 9) | (g << 6) | (b << 3)
		integer=(a*0x1FE00) | rgb | ((rgb >> 5) & 0x070707)
		newdata+=struct.pack('I',integer)
	return newdata

class Image():
	def __init__(self):
		self.format=None
		self.wys=None
		self.szer=None
		self.name=None
		self.data=None

	def draw(self):
		if None not in (self.format, self.wys, self.szer, self.name,self.data):
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
				rgb565_to_rgb888(self.szer,self.wys,self.data,self.name)
			else:
				print 'warning: unknown format',self.format