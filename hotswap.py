import SimpleCV
import sys

DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480
CENTER = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2)
MIN_AREA = 2500

def display_overlay(img, biggest_blob, normaldisplay, segmented_red):
	""" Displays the camera image in the display. Also sets up 
			mouse clicks to switch between display modes 
	"""
	if normaldisplay == 1:
		if biggest_blob != None:
			biggest_blob.draw((255,0,0))
		segmented_red.show()
	else:
		img.show()

def vector_to_center(img, x_y, color=(0,255,0), strength=5, varying_strength=True):
	""" Draws a vector to the center of the screen to indicate how far from the 
		center we are
	"""
	img.drawLine(x_y, CENTER, color, strength)

def border(img, color=(0,255,0), strength=15):
	""" Draws a line around the bodrer of the screen """
	img.drawRectangle(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, color, strength)

def abs_distance(tuple1, tuple2):
	""" Returns the absolute difference between point of tuple1 and tuple2 """
	return ((tuple2[0] - tuple1[0]) ** 2 + (tuple2[1] - tuple1[1]) ** 2) ** (0.5)

def check_position(img, blob):	
	""" If the center of our screen is in the largest blob, we turn the border green.
		If not but we turn the screen red.
	"""				
	if blob.contains(CENTER):
		border(img)
	else:
		border(img, (255,0,0))

def draw_hull(img, blob):
	""" Draws a convex hull of the blob. """
	list_of_points = blob.hull()
	tempx = list_of_points[0][0]
	tempy = list_of_points[0][1]
	for x1,y1 in list_of_points:
		img.drawLine((tempx,tempy), (x1,y1), SimpleCV.Color.CYAN, 3)
		tempx=x1
		tempy=y1

def display_distance(img, blob=None):
	""" Draws text on the img layer displaying the distance from the object. """ 
	# TODO FIGURE OUT DISANCE:
	txt = "Distance: N/A" 
	if blob:
		txt = "Distance: " + str(blob.area())
	text_layer = SimpleCV.DrawingLayer((DISPLAY_WIDTH, DISPLAY_HEIGHT))
	text_layer.ezViewText(txt, (20,20), (0,0,0), (255,255,255))
	img.addDrawingLayer(text_layer)

def display_orientation(img, blob=None):
	""" Draws text on the img layer displaying the orientation from the object. """ 
	# TODO FIGURE OUT Orientation:
	txt = "Orientation: N/A"
	if blob:
		txt = "Orientation: " + str(blob.width())
	text_layer = SimpleCV.DrawingLayer((DISPLAY_WIDTH, DISPLAY_HEIGHT))
	text_layer.ezViewText(txt, (20,40), (0,0,0), (255,255,255))
	img.addDrawingLayer(text_layer)

def run(cam=SimpleCV.Camera(0)):
	display = SimpleCV.Display()
	normaldisplay = 0
	hull = False

	while display.isNotDone():
		if display.mouseRight:
			normaldisplay = (normaldisplay + 1) % 2
		if display.mouseLeft:
			hull = not(hull)
		img = cam.getImage().flipHorizontal()
		
		# Option 1
		away_from_red = img.colorDistance((255,0,0))
		only_red = img - away_from_red
		segmented_red = only_red.erode(5).binarize().invert()

		display_distance(img)
		display_orientation(img)
		
		biggest_blob = None
		blobs = segmented_red.findBlobs()
		if blobs:
			squares = blobs.filter([b.isRectangle(0.13) for b in blobs])
			if squares:
				largest_square = squares[-1]
				biggest_blob = largest_square
				if largest_square.area() >= MIN_AREA:
					width = largest_square.width()
					height = largest_square.height()
					x1 = largest_square.x - (width / 2)
					y1 = largest_square.y - (height /2)

					display_distance(img, largest_square)
					display_orientation(img, largest_square)

					# Guidance 
					vector_to_center(img, largest_square.centroid())
					check_position(img, largest_square)
					# Use for convex hull instead of rectangle
					if hull:
						draw_hull(img, largest_square)
					else:
						img.drawRectangle(x1, y1, width, height, SimpleCV.Color.BLUE, 3)

					img.drawCircle((largest_square.x,largest_square.y), 3, SimpleCV.Color.BLUE, 3)

		display_overlay(img, biggest_blob, normaldisplay, segmented_red)
			

if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1] != "--ip":
			print "System arguments: --ip [for web camera]"
			exit(0)
		address = "admin:admin@192.168.29.206:8081/video"
		cam = SimpleCV.JpegStreamCamera(address)
		run(cam)
	else:
		run()
