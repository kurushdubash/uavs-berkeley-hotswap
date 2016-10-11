import SimpleCV

display = SimpleCV.Display()
cam = SimpleCV.Camera(0)
# address = "admin:admin@192.168.29.206:8081/video"
# cam = SimpleCV.JpegStreamCamera(address)
normaldisplay = 0
hull = False
MIN_AREA = 2500
while display.isNotDone():

	if display.mouseRight:
		normaldisplay = (normaldisplay + 1) % 3 

	if display.mouseLeft:
		hull = not(hull)

	img = cam.getImage().flipHorizontal()
	
	# Option 1
	away_from_red = img.colorDistance((255,0,0))
	only_red = img - away_from_red
	segmented_red = only_red.erode(5).binarize().invert()
	
	# away_from_cyan = img.colorDistance((0,255,255))
	# only_cyan = img - away_from_cyan
	# segmented_cyan = only_cyan.erode(5).binarize().invert()
	
	# Option 2
	# dist = img.hueDistance(SimpleCV.Color.BLACK).dilate(2).invert()
	# segmented = dist.stretch(220,255)
	square_found = False
	biggest_blob = None
	blobs = segmented_red.findBlobs()
	if blobs:
		squares = blobs.filter([b.isRectangle(0.13) for b in blobs])
		if squares:
			square_found = True
			largest_square = squares[-1]
			biggest_blob = largest_square
			if largest_square.area() >= MIN_AREA:
				width = largest_square.width()
				height = largest_square.height()
				x = largest_square.x - (width / 2)
				y = largest_square.y - (height /2) 

				# Use for convex hull instead of rectangle
				if hull:
					list_of_points = largest_square.hull()
					tempx = list_of_points[0][0]
					tempy = list_of_points[0][1]
					for x1,y1 in list_of_points:
						img.drawLine((tempx,tempy), (x1,y1), SimpleCV.Color.CYAN, 3)
						tempx=x1
						tempy=y1
				else:
					img.drawRectangle(x, y, width, height, SimpleCV.Color.BLUE, 3)
				img.drawCircle((largest_square.x,largest_square.y), 3, SimpleCV.Color.BLUE, 3)
	# circles = segmented_cyan.findBlobs()
	# if circles and square_found:
		# circle = circles.filter([c.isCircle(0.13) for c in circles])
		# if circle:
		# 	largest_circle = circle[-1]
		# 	img.drawCircle((largest_circle.x,largest_circle.y), 3, SimpleCV.Color.BLUE, 3)
		# 	img.drawCircle((largest_circle.x,largest_circle.y), largest_circle.radius(), SimpleCV.Color.BLUE, 3)

	if normaldisplay == 2:
		segmented_cyan.show()
	elif normaldisplay == 1:
		if biggest_blob != None:
			biggest_blob.draw((255,0,0))
		segmented_red.show()
	else:
		img.show()
