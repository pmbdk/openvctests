# import the necessary packages
from collections import deque
import numpy as np
import argparse
#import imutils
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# When setting HSV colors, remeber, that they should be scaled
# Normal: H 0-360, S 0-100, V 0-100
# OpenCV: H 0-180, S 0-255, V 0-255

# Green
#colorLower = (103/2-10, 150, 150)
#colorUpper = (103/2+10, 255, 255)

# Yellow
colorLower = ((54 - 20)/2, ( 89 - 20 ) * 255/100, (74 - 50) * 255/100)
colorUpper = ((54 + 20)/2, ( 89 + 11 ) * 255/100, (74 + 26) * 255/100)
pts = deque(maxlen=args["buffer"])


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 60
#camera.brightness = 70
camera.iso = 400

rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)
counter = 0
saveCounter = 0

# fourcc = cv2.cv.CV_FOURCC(*"XVID")
motion_filename = "testvid.avi"
motion_file = cv2.VideoWriter(motion_filename, cv2.VideoWriter_fourcc(*'MJPG'), 1.0, camera.resolution)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        counter += 1
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array

	# resize the frame, blur it, and convert it to the HSV
	# color space
	# frame = imutils.resize(frame, width=600)
	# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, colorLower, colorUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)	
	
	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None
	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(image, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(image, center, 5, (0, 0, 255), -1)

	# update the points queue
	pts.appendleft(center)
	# loop over the set of tracked points
	for i in xrange(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(image, pts[i - 1], pts[i], (0, 0, 255), thickness)
	
	
	
	
	# show the frame
	# Limit frame shown
	# if ( counter & 0x07 ) == 0:
        cv2.imshow("Frame", image)
        motion_file.write(image)
	key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
	if key == ord("s"):
		cv2.imwrite('testimg' + str( saveCounter ) + '.png', image )
		saveCounter += 1
	    
# cleanup the camera and close any open windows
motion_file.release()
camera.release()
cv2.destroyAllWindows()
	    
	    
	    
