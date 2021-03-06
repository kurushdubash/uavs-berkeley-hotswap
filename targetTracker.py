import cv2
import urllib
import urllib.request
import numpy as np
import math, sys
import time

APERTURE_ANGLE = 30.0 * math.pi / 180.0 #radians
LONGSIDE_ACTUAL = 4.0 #inches rn
SCALE = 8.0 #for scaling arrow vector
OFF_TARGET_TOLERANCE = 10 #pixel difference from center of target to consider on/off target; also used as radius
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
BOUNDING_RATIO = 1.675
cent = (FRAME_WIDTH//2, FRAME_HEIGHT//2)

# worked the best -- run averages.py to see average times for the 4 detectors I tried
detector = cv2.BRISK_create() #cv2.xfeatures2d.BriefDescriptorExtractor_create() #ORB_create()#SURF_create(300)

# distance between two tuple points
def distance(p1, p2):
    return pow ( pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2), 0.5 )

#return the angle of the rectangle in STRING form (for outputting) .. todo implement correctly
def angleOfRect(image, rect):
    ((x,y), (width, height), angle) = rect
    return "{0:.2f}".format(angle)

#draws an arrow on the image
def drawArrow(image, correctionVec, magnitude):
    norm = (SCALE / magnitude * correctionVec[0],  SCALE / magnitude * correctionVec[1])
    #  [ 1/rt(2) -1/rt(2)  ;  1/rt(2) 1/rt(2) ] * scaled_vec
    shift1 = (norm[0]/math.sqrt(2) - norm[1]/math.sqrt(2),
                        norm[0]/math.sqrt(2) + norm[1]/math.sqrt(2))
    shift2 = (norm[0]/math.sqrt(2) + norm[1]/math.sqrt(2),
                        - norm[0]/math.sqrt(2) + norm[1]/math.sqrt(2))

    cv2.line( image, (cent[0] + correctionVec[0],cent[1] + correctionVec[1]) , cent, (0,0,255), 2)
    cv2.line( image, cent, (cent[0] + int(shift1[0]), cent[1] + int(shift1[1])), (0,0,255),2)
    cv2.line( image, cent, (cent[0] + int(shift2[0]), cent[1] + int(shift2[1])), (0,0,255),2)

    return image

#draw the rotated rect on the inputted image
def drawRotatedRect(image, rect_points, color=(0,0,255), thickness=2):
    for j in range(4):
        cv2.line(image, rect_points[j], rect_points[(j+1)%4], color, thickness)
        # cv2.line( original, tuple(rect_points[j]), tuple(rect_points[(j+1)%4]), (0,0,255), 2)
        # cv2.line( img_matches, (int(rect_points[j][0] + logo.shape[1]), int(rect_points[j][1])), 
        #     (int(rect_points[(j+1)%4][0] + logo.shape[1]), int(rect_points[(j+1)%4][1])), (255, 0, 255), 4);
    return image

# is the rectangle of a certain ratio (l:w)
def withinRatioTol(rect):
    ((x,y), (width, height), angle) = rect
    return False if width == 0 or height == 0 else abs(width / height - BOUNDING_RATIO) < 0.2 or abs(height / width - BOUNDING_RATIO) < 0.2

# get the rect's distance (represented as correction vector) and the distance
def rectCorrectionVecAndDistance(rect):
    ((x,y), (width, height), angle) = rect
    longside_pix = max(width, height)
    return (int(x-cent[0]), int(y-cent[1])), FRAME_WIDTH * LONGSIDE_ACTUAL / longside_pix / (2 * math.tan(APERTURE_ANGLE));

#filter the matches to the most representative ones and return that
def filterMatches(matches, keypoint_obj, keypoints_scene):

    max_dist, min_dist = 0,100

    # print(descriptors_obj)
    # print(descriptors_scene)
    # print(matches)

    # find max and min distance
    for match in matches:
        if len(match) > 0:
            dist = match[0].distance
            if dist < min_dist: 
                min_dist = dist
            if dist > max_dist:
                max_dist = dist

    # only get the matches for which there is an actual match happening
    medium_matches = []
    scene_raw = []
    for match in matches:
        if len(match) > 0:
            query = match[0].queryIdx
            train = match[0].trainIdx
            if query < len(keypoint_obj) and train < len(keypoints_scene): #and match[0].distance < 0.98 * match[1].distance:
                medium_matches.append(match[0])
                scene_raw.append( keypoints_scene[train].pt )
    
    # for filtering based on distance away from mean point
    mean_x = int(sum([x for x,y in scene_raw])/len(scene_raw))
    mean_y = int(sum([y for x,y in scene_raw])/len(scene_raw))

    # print(distance)
    distances = [ distance(pt, (mean_x, mean_y)) for pt in scene_raw]
    distances = sorted(distances)
    maxDist = distances[-1]
    #median distance from the mean point
    medianDist = distances[len(distances)//2]
    # halfway between the medianDist and the maxDist
    threshDist = medianDist + (maxDist-medianDist)/2

    obj = []
    scene = []

    good_matches = []

    #filter based on the max dist and the distance to mean point (in comparison to recently calculated thresh point)
    for match in medium_matches:
        pt_obj = keypoint_obj[ match.queryIdx ].pt
        pt_scene = keypoints_scene[ match.trainIdx ].pt

        if match.distance < 0.80 * max_dist and distance((mean_x, mean_y), pt_scene) < threshDist:
            good_matches.append(match)
            obj.append(pt_obj)
            scene.append(pt_scene)

    obj = np.array(obj)
    scene = np.array(scene)

    return good_matches, obj, scene, mean_x, mean_y

# fill images with rectangles, arrows, text, etc about the inputted rect
def populateImages(original, img_matches, rect):
    rect_points = cv2.boxPoints(rect)
    rect_points = [ (int(pt[0]), int(pt[1])) for pt in rect_points ]

    # get the distance away and the correction vector
    correctionVec, dist = rectCorrectionVecAndDistance(rect)
    # TODO implement
    angle = angleOfRect(original, rect)

    mag = distance((0,0), correctionVec)
    
    if mag < OFF_TARGET_TOLERANCE:
        cv2.circle(original, cent, OFF_TARGET_TOLERANCE, (0,255,0), 3)
    else:
        original = drawArrow(original, correctionVec, mag)

    cv2.putText(original, "Distance: " + "{0:.2f}".format(dist) + "   Angle: " + angle, (40,40), cv2.FONT_HERSHEY_PLAIN, 0.8, (0,255,0), 2)

    original = drawRotatedRect(original, rect_points)
    img_matches = drawRotatedRect(img_matches, [ (x + logo.shape[1], y) for x,y in rect_points])

    return original, img_matches, correctionVec, angle

# run the feature detection, find matches, find homography, perspectiveTransform, draw the rectangles and arrows, and return back populated image
def processFeatures(original, logo, keypoint_obj, descriptors_obj):

    m = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

    keypoints_scene, descriptors_scene = detector.detectAndCompute(m, None)

    matcher = cv2.BFMatcher(cv2.NORM_L2, True)
    matches = matcher.knnMatch(descriptors_obj, descriptors_scene, k=1)

    good_matches, obj, scene, mean_x, mean_y = filterMatches(matches, keypoint_obj, keypoints_scene)

    img_matches = None

    dist = None
    correctionVec = None
    angle = None

    if len(good_matches) > 4:
        #finally done filtering
        # print(good_matches)
        img_matches = cv2.drawMatches( logo, keypoint_obj, original, keypoints_scene, matches1to2=good_matches, outImg=None, flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)

        cv2.circle(img_matches, (mean_x + logo.shape[1], mean_y), 10, (0,0,255), 2)

        #proceed if we have good matches
        H, mask = cv2.findHomography(obj, scene, method=cv2.RANSAC)

        #get the corners of the logo image
        logo_corners = np.array([[0,0], [logo.shape[1], 0], [logo.shape[1], logo.shape[0]], [0, logo.shape[0]]], dtype='float32')
        logo_corners = np.array([logo_corners])

        if H is not None and H.shape[0] > 1:
            #if there is a homography mat to use, use it
            scene_corners = cv2.perspectiveTransform(logo_corners, H)
            rect = cv2.minAreaRect(scene_corners)

            if withinRatioTol(rect):
                #draw everything including arrows
                original, img_matches, correctionVec, angle = populateImages(original, img_matches, rect)

    return original, correctionVec, dist, angle

# TODO: when we have MAVLINK and stuff set up to respond to inputted distance
def autoLandAdjust(image, correctionVec, dist, angle):
    #do something here eventually
    return

#read the frame from a byte stream
def get_frame(stream):
    bytes=b''
    # count = 0
    # startTime = time.time()
    while True:
        # count += 1
        bytes+=stream.read(1024)
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes= bytes[b+2:]
            # print(jpg)
            if jpg != b'':
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                # print(count, time.time() - startTime)
                return i


# continuous loop!
if __name__ == "__main__":
    # cv2.ocl.setUseOpenCL(False)

    print("######### PYTHON DETECTION STARTING ########\n")

    # loading the comparison image
    logo = cv2.imread('cal_logo_uavs.png', cv2.IMREAD_GRAYSCALE)
    keypoints_obj, descriptors_obj = detector.detectAndCompute(logo, None)          

    cv2.namedWindow('Image',cv2.WND_PROP_FULLSCREEN)

    ip=False
    stream=""

    # load the vid stream if we pass in --ip
    if len(sys.argv) > 1:
        if sys.argv[1] != "--ip":
            print("System arguments: --ip [for web camera]")
            exit(0)
        stream=urllib.request.urlopen('http://192.168.0.101:8081/video')
        ip=True

    # read from default video capture if not
    if not ip:
        cap = cv2.VideoCapture(0) 

    while(True):
        # Capture frame-by-frame
        if not ip:
            ret, original = cap.read()
        else:
            original = get_frame(stream)

        #if the frame is inputted and exists, resize, 
        if original is not None and original.shape[0] > 1:        
            # frame width and frame height scaled globally
            FRAME_WIDTH = int(original.shape[1]/1.6)
            FRAME_HEIGHT = int(original.shape[0]/1.6)
            #center of frame
            cent = (FRAME_WIDTH//2, FRAME_HEIGHT//2)

            # resize image to be maneagable in computation
            original = cv2.resize(original, (FRAME_WIDTH, FRAME_HEIGHT))

            # match detector features and draw found objects to original
            # start = time.time()
            original, correctionVec, dist, angle = processFeatures(original, logo, keypoints_obj, descriptors_obj)
            # print(time.time() - start)

            #the eventual drone adjustment aspect of the code
            if correctionVec is not None and angle is not None:
                autoLandAdjust(original, correctionVec, dist, angle)

            # original = cv2.resize(original, (FRAME_WIDTH*2, FRAME_HEIGHT*2))
            cv2.imshow('Image',original)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # When everything done, release the capture
    if not ip:
        cap.release()
    cv2.destroyAllWindows()



