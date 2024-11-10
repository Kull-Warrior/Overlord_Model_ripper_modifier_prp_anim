import struct
import Blender

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