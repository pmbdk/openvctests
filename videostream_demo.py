# import the necessary packages
from imutils.video import VideoStream
import datetime
import argparse
import imutils
import time
import cv2
from imutils.video import FPS


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", type=int, default=1,
	help="whether or not the Raspberry Pi camera should be used")
args = vars(ap.parse_args())

# initialize the video stream and allow the cammera sensor to warmup
vs = VideoStream( usePiCamera=args["picamera"] > 0, resolution=(320, 240),	framerate=60 ).start()
time.sleep(2.0)
fps = FPS().start()

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of X pixels
	frame = vs.read()
	
	# No need to resize if the stream is already the correct size...
	#frame = imutils.resize(frame, width=320)

	# Rotate (we could do that during read to improve performance)
#	frame = imutils.rotate( frame, 180 )

        # Lets try openCV flip instead, performs 3-4 times faster!
        frame = cv2.flip( frame, -1 )

	# draw the timestamp on the frame
	# No need...
##	timestamp = datetime.datetime.now()
##	ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
##	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
##		0.35, (0, 0, 255), 1)

	# show the frame
	cv2.imshow("Frame", frame)
	fps.update()
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

fps.stop()
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
