'''
This is how to track a white ball example using SimpleCV
The parameters may need to be adjusted to match the RGB color
of your object.
The demo video can be found at:
http://www.youtube.com/watch?v=jihxqg3kr-g
'''
print __doc__

import SimpleCV

display = SimpleCV.Display()
cam = SimpleCV.Camera(0)
normaldisplay = True

while display.isNotDone():

	if display.mouseRight:
		normaldisplay = not(normaldisplay)
		print "Display Mode:", "Normal" if normaldisplay else "Segmented" 
	
	img = cam.getImage().flipHorizontal()
	dist = img.hueDistance(SimpleCV.Color.BLACK).dilate(2).invert()
	segmented = dist.stretch(220,255)
	blobs = segmented.findBlobs()
	if blobs:
		squares = blobs.filter([b.isRectangle(0.2) for b in blobs])
		if squares:
			big = squares[-1]
			width = squares[-1].width()
			height = squares[-1].height()
			x = squares[-1].x - (width / 2)
			y = squares[-1].y - (height /2) 
			img.drawRectangle(x, y, width, height, SimpleCV.Color.BLUE, 3)

	if normaldisplay:
		img.show()
	else:
		segmented.show()
