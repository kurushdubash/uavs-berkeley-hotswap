import SimpleCV

display = SimpleCV.Display()
cam = SimpleCV.Camera(0)
# address = "admin:admin@192.168.29.206:8081/video"
# cam = SimpleCV.JpegStreamCamera(address)
normaldisplay = True
MIN_AREA = 2500
while display.isNotDone():

	if display.mouseRight:
		normaldisplay = not(normaldisplay)
		print "Display Mode:", "Normal" if normaldisplay else "Segmented" 
	
	img = cam.getImage().flipHorizontal()
	dist = img.hueDistance(SimpleCV.Color.BLACK).dilate(1).invert()
	segmented = dist.stretch(235,255)
	blobs = segmented.findBlobs()
	if blobs:
		squares = blobs.filter([b.isRectangle(0.2) for b in blobs])
		if squares:
			largest_square = squares[-1]
			if largest_square.area() >= MIN_AREA:
				width = largest_square.width()
				height = largest_square.height()
				x = largest_square.x - (width / 2)
				y = largest_square.y - (height /2) 
				# img.drawLine((x,y), (x,y+height), SimpleCV.Color.BLUE, 3)
				# img.drawLine((x,y), (x+width,y), SimpleCV.Color.BLUE, 3)
				# img.drawLine((x,y+height), (x+width,y+height), SimpleCV.Color.BLUE, 3)
				# img.drawLine((x+width,y+height), (x+width,y), SimpleCV.Color.BLUE, 3)
				# print largest_square.area()
				img.drawRectangle(x, y, width, height, SimpleCV.Color.BLUE, 3)
				img.drawCircle((largest_square.x,largest_square.y), 3, SimpleCV.Color.BLUE, 3)
	if normaldisplay:
		img.show()
	else:
		segmented.show()
