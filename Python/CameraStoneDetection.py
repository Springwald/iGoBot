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
	
	__cameraResolutionX 		= 640*2
	__cameraResolutionY 		= 480*2
	
	_windowName 				= "iGoBot camera";
	
	RectsBlack					= [];
	RectsWhite					= [];
	
	_counter					= 0;
	
	_released					= False

	def __init__(self):
		print("camera init")
		self.posXFace = -1
		self.posYFace = -1
		self.InitCamera();
		
	def detect(self, img, cascade):
		rects = cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=3, minSize=(int(self.__cameraResolutionX / 30), int( self.__cameraResolutionY / 30)), flags=cv2.CASCADE_SCALE_IMAGE)
		if len(rects) == 0:
			return []
		#rects[:,2:] += rects[:,:2] # convert from [[x,y,h,b]] to [[x1,y1,x2,y2]]
		return rects

	def draw_rects(self, img, rects, color):
		for x, y, b, h in rects:
			cv2.rectangle(img, (x, y), (x+b, y+h), color, 4)
			
	def InitCamera(self):
		print("camera start")
		
		cv2.destroyAllWindows()
		cv2.namedWindow(self._windowName, cv2.WINDOW_NORMAL)
		cv2.resizeWindow(self._windowName, 400,300)
		
		# initialize the camera and grab a reference to the raw camera capture
		self._camera = PiCamera()
		self._camera.resolution = (self.__cameraResolutionX, self.__cameraResolutionY)
		self._camera.contrast = 50;
		self._camera.brightness = 50;
		self._camera.framerate = 12
		self._rawCapture = PiRGBArray(self._camera, size=(self.__cameraResolutionX, self.__cameraResolutionY))
		
		# allow the camera to warmup
		time.sleep(0.1)
		
		cascade_black_fn =  "stoneDetection/black-cascade.xml"
		cascade_white_fn =  "stoneDetection/white-cascade.xml"
		self._cascadeBlack = cv2.CascadeClassifier(cascade_black_fn)
		self._cascadeWhite = cv2.CascadeClassifier(cascade_white_fn)

		print("camera start done")
			
	def Update(self):
		
		# capture frames from the camera
		for frame in self._camera.capture_continuous(self._rawCapture, format="bgr", use_video_port=True):
		#if (True):
		#	frame = self._camera.capture(self._rawCapture, format="bgr")
			# grab the raw NumPy array representing the image - this array
			# will be 3D, representing the width, height, and # of channels
			#image = frame.array
		 
			key = cv2.waitKey(1) & 0xFF
		 
			## clear the stream in preparation for the next frame
			self._rawCapture.truncate(0)
		 
			# local modules
			#from video import create_capture
			#from common import clock, draw_str
			
			self._camera.capture(self._rawCapture, format="bgr")
			image = self._rawCapture.array
					
			# clear the stream in preparation for the next frame
			self._rawCapture.truncate(0)

			#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			#gray = cv2.equalizeHist(gray)
			self.RectsBlack = self.detect(image, self._cascadeBlack)
			self.RectsWhite = self.detect(image, self._cascadeWhite)
					
			self._counter = self._counter+1;
			#print (self._counter);
			if (self._counter > 100):
				self._counter = 0;
					
			if (self._showImage==True):
				self.draw_rects(image, self.RectsBlack, (0, 0, 0))
				self.draw_rects(image, self.RectsWhite, (255, 255, 255))
				cv2.putText(image, str(self._counter), (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
				cv2.imshow(self._windowName, image)
				
			#break;

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down camera")

	def __del__(self):
			self.Release()

if __name__ == '__main__':

	testCamera = CameraStoneDetection();

	for c in range(0,30):
		testCamera.Update();
		time.sleep(0.1)
		
	#while (True):
	#	time.sleep(1);
