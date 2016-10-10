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
	dist = img.hueDistance(SimpleCV.Color.BLACK).dilate(2).invert()
	segmented = dist.stretch(235,255)
	blobs = segmented.findBlobs()
	if blobs:
		squares = blobs.filter([b.isRectangle(0.15) for b in blobs])
		if squares:
			largest_square = squares[-1]
			if largest_square.area() >= MIN_AREA:
				width = largest_square.width()
				height = largest_square.height()
				x = largest_square.x - (width / 2)
				y = largest_square.y - (height /2) 

				# Use for convex hull instead of rectangle
				# list_of_points = largest_square.hull()
				# tempx = list_of_points[0][0]
				# tempy = list_of_points[0][1]
				# for x1,y1 in list_of_points:
				# 	img.drawLine((tempx,tempy), (x1,y1), SimpleCV.Color.BLUE, 3)
				# 	tempx=x1
				# 	tempy=y1

				img.drawRectangle(x, y, width, height, SimpleCV.Color.BLUE, 3)
				img.drawCircle((largest_square.x,largest_square.y), 3, SimpleCV.Color.BLUE, 3)
	if normaldisplay:
		img.show()
	else:
		segmented.show()
