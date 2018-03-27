#!/usr/bin/env python


#     #############################
#     # GO stone camera detection #
#     #############################
#
#     Licensed under MIT License (MIT)
#
#     Copyright (c) 2018 Daniel Springwald | daniel@springwald.de
#
#     Permission is hereby granted, free of charge, to any person obtaining
#     a copy of this software and associated documentation files (the
#     "Software"), to deal in the Software without restriction, including
#     without limitation the rights to use, copy, modify, merge, publish,
#     distribute, sublicense, and/or sell copies of the Software, and to permit
#     persons to whom the Software is furnished to do so, subject to
#     the following conditions:
#
#     The above copyright notice and this permission notice shall be
#     included in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#     THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#     DEALINGS IN THE SOFTWARE.

import os, sys

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/libs" )
sys.path.insert(0,my_path + "/libs/opencv" )

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

class CameraStoneDetection():

	_showImage					= True
	
	_camera						= None
	_rawCapture					= None
	
	_cascadeBlack				= None
	_cascadeWhite				= None

	__cameraResolutionX 		= 640
	__cameraResolutionY 		= 480
	
	posXFace = 0;#-1 # -1=no face, 0=max left, 1=max right
	posYFace = 0;#-1 # -1=no face, 0=max bottom, 1=max top

	_released						= False
	
	_delay_seconds				= 1

	def __init__(self):
		print("camera init")
		self.posXFace = -1
		self.posYFace = -1
		
		
	def detect(self, img, cascade):
		rects = cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=3, minSize=(int(self.__cameraResolutionX / 40), int( self.__cameraResolutionY / 40)), flags=cv2.CASCADE_SCALE_IMAGE)
		if len(rects) == 0:
			return []
		rects[:,2:] += rects[:,:2]
		return rects

	def draw_rects(self, img, rects, color):
		for x1, y1, x2, y2 in rects:
			#print("detected");
			cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
			
			
	def Update(self):
		
		print("camera start")
		
		cv2.destroyAllWindows()
		
		# initialize the camera and grab a reference to the raw camera capture
		self._camera = PiCamera()
		self._camera.resolution = (self.__cameraResolutionX, self.__cameraResolutionY)
		self._camera.contrast = 60;
		self._camera.brightness = 50;
		self._camera.framerate = 8
		self._rawCapture = PiRGBArray(self._camera, size=(self._camera.resolution.width, self._camera.resolution.height))
		
		# allow the camera to warmup
		time.sleep(0.1)
		
		cascade_black_fn =  "stoneDetection/black-cascade.xml"
		cascade_white_fn =  "stoneDetection/white-cascade.xml"
		self._cascadeBlack = cv2.CascadeClassifier(cascade_black_fn)
		self._cascadeWhite = cv2.CascadeClassifier(cascade_white_fn)
		
		# capture frames from the camera
		for frame in self._camera.capture_continuous(self._rawCapture, format="bgr", use_video_port=True):
			# grab the raw NumPy array representing the image - this array
			# will be 3D, representing the width, height, and # of channels
			image = frame.array
		 
			# show the frame
			#cv2.imshow("Frame", image)
			key = cv2.waitKey(1) & 0xFF
		 
			## clear the stream in preparation for the next frame
			self._rawCapture.truncate(0)
		 
			## if the `q` key was pressed, break from the loop
			if key == ord("q"):
				break

			# local modules
			#from video import create_capture
			from common import clock, draw_str
			
			self._camera.capture(self._rawCapture, format="bgr")
			image = self._rawCapture.array
					
			# clear the stream in preparation for the next frame
			self._rawCapture.truncate(0)

			#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			#gray = cv2.equalizeHist(gray)
			rects = self.detect(image, self._cascadeBlack)
					
			if (self._showImage==True):
				vis = image.copy()
				self.draw_rects(vis, rects, (0, 255, 0))
				cv2.imshow("stone detection", vis)

	def ResetFace(self):
		self.posXFace = -1
		self.posYFace = -1

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down camera")
			#super().EndUpdating()

	def __del__(self):
			self.Release()

if __name__ == '__main__':
	
	testCamera = CameraStoneDetection();
	
	
	while (True):
		testCamera.Update();
		if (testCamera.posXFace != -1):
			print(str(testCamera.posXFace) + " / " + str(testCamera.posYFace))
			testCamera.ResetFace()
		time.sleep(0.01)
