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

class Image():
	def __init__(self):
		self.format=None
		self.height=None
		self.width=None
		self.name=None
		self.data=""