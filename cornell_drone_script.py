from SimpleCV import *
import time
import math
import thread
from time import sleep
mpstate = None
def cameraDetection():
	global mpstate
	disp = Display()
	#cam = Camera(0)
	address = 'admin:admin@192.168.29.206:8081/video'
	cam = JpegStreamCamera(address)
	print address

 #f.close()

	xmin = 0 #310
	xmax = 640 #420
	ymin = 0 #160
	ymax = 480 #320
	blobmin = 2000 #2000`
	while disp.isNotDone():
		# override = mpstate.status.override[:]
		img = cam.getImage()
		if img != None:
			red_img_dist = img.colorDistance((255,0,0))
			bin_img = red_img_dist.binarize(100)
			blobs = bin_img.findBlobs()
			if blobs != None:
				biggestblob = blobs[-1]
				biggestblob.draw(color =(255,0,0))
				print biggestblob.area()
				if biggestblob.area() > blobmin:
					loc = biggestblob.centroid()
					# print loc
					if biggestblob.isRectangle(tolerance = 0.051):
						distance = 12389*math.pow(biggestblob.length(),-0.976)
						print "The ground is " + str(distance) + " cm away"
					# if (biggestblob.x > xmin) and (biggestblob.x < xmax):
					# 	if (biggestblob.y > ymin) and (biggestblob.y < ymax):
					# 		print "idk"
							#override[4] = 1000
							# mpstate.status.override = override
							# mpstate.override_period.force()
			img.show()
			bin_img.save(disp)
def name():
	return "android"
def description():	
	return "Android Camera Computer Vision"
def mavlink_packet(pkt):
	pass
def init(_mpstate):
	global mpstate
	print "Start Camera init"

	# mpstate = _mpstate
	cameraDetection()
	thread.start_new_thread(cameraDetection, ())
	# state = module_state()
	# mpstate.androidcam_state = state
	print "End camera init"

init("test")