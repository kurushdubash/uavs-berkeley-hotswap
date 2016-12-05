from SimpleCV import *
import time
# address = "admin:admin@192.168.29.206:8081/video"
# cam = JpegStreamCamera(address)
cam = Camera(0)
display = Display()
count = 0
while display.isNotDone():
	img = cam.getImage()
	facedetect = img.findHaarFeatures('face2.xml')
	if img == None:
		continue
	if facedetect:
		facedetect.draw()
	img.show()
	# time.sleep(.01)
	count += 1
	if count == 1000:
		break