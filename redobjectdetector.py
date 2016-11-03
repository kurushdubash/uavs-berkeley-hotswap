import cv2
import numpy as np

KNOWN_WIDTH = 3.5

def drawRect(max_cnt, frame):
    rect = cv2.minAreaRect(max_cnt)
    box = cv2.cv.BoxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(frame,[box],0,(0,0,255),2)
    return rect

def distance_to_camera(knownWidth, focalLength, pixWidth):
	# compute and return the distance from the maker to the camera
	return (knownWidth * focalLength) / pixWidth

def distance(image, cnt):
	marker = cv2.minAreaRect(cnt)
	return distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])

def morphOps(mask):
    kernel = np.ones((5, 5),np.uint8)
    output = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    output = cv2.morphologyEx(output, cv2.MORPH_CLOSE, kernel)
    return output

def find_marker(image):
	# convert the image to grayscale, blur it, and detect edges
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(gray, 35, 125)

	# find the contours in the edged image and keep the largest one;
	# we'll assume that this is our piece of paper in the image
	(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	max_cnt = max(cnts, key = cv2.contourArea)

	# compute the bounding box of the of the paper region and return it
	return max_cnt

def display_blob(max_cnt, image):
    box = drawRect(max_cnt, image)
    inches = distance(box, max_cnt)
    cv2.putText(image, "%.2fft" % (inches / 12),
        (image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
        2.0, (0, 255, 0), 3)
    M = cv2.moments(max_cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    (x,y),(MA,ma),angle = cv2.fitEllipse(max_cnt)
    cv2.putText(image, str(cx) + ", " + str(cy), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

# initialize the known object width (in inches) and focal length of camera
KNOWN_WIDTH = 3.5
focalLength = 586.285714286

cap = cv2.VideoCapture(0)

while(True):
    ret, frame = cap.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # create NumPy arrays from the boundaries
    lower = np.array([158, 94, 112], dtype = "uint8")
    upper = np.array([179, 255, 255], dtype = "uint8")

	# find the colors within the specified boundaries and apply
	# the mask
    mask = cv2.inRange(hsv, lower, upper)
    mask = morphOps(mask)

    #find the contours in the image
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #if contours were found then find the contour with the largest area and perform calculations for distance and centroid position
    if contours:
        max_cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(max_cnt) > 1000:
            display_blob(max_cnt, frame)

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

#TODO

#centroid of the blob
#centroid of the frame
#vector from centroid of the frame to centroid of the blob
