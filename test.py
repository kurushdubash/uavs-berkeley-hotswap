from SimpleCV import *
import time
# address = "admin:admin@192.168.29.206:8081/video"
# cam = JpegStreamCamera(address)
cam = Camera(0)
display = Display()
count = 0
while display.isNotDone():
	img = cam.getImage()
	img2 = img.hueDistance(color=Color.RED).binarize(128)
	img2 = img2.binarize(blocksize=3,p=1)
	img3 = img.sideBySide(img2)
	# facedetect = img.findHaarFeatures('face2.xml')
	if img == None:
		continue
	# if facedetect:
		# facedetect.draw()
	# img = img.erode()
	img3.show()
	# time.sleep(.01)
	count += 1
	if count == 1000:
		break