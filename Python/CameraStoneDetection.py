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
	
	_cascade					= None
	_nested						= None
	
	__cameraResolutionX 		= 640
	__cameraResolutionY 		= 480
	
	posXFace = 0;
	posYFace = 0;

	__posXFaceKey 				= MultiProcessing.get_next_key() #-1 # -1=no face, 0=max left, 1=max right
	__posYFaceKey 				= MultiProcessing.get_next_key() #-1 # -1=no face, 0=max bottom, 1=max top
	
	_released						= False
	
	_delay_seconds				= 1
	_delay_seconds_when_idle	= 1.5

	def __init__(self):
		print("camera init")
		self.posXFace = -1
		self.posYFace = -1
		
		
	def detect(self, img, cascade):
		rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=3, minSize=(int(self.__cameraResolutionX / 15), int( self.__cameraResolutionY / 15)), flags=cv2.CASCADE_SCALE_IMAGE)
		if len(rects) == 0:
			return []
		rects[:,2:] += rects[:,:2]
		return rects

	def draw_rects(self, img, rects, color):
		for x1, y1, x2, y2 in rects:
			cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
			
			
	def Update(self):
		
		print("camera start")
		
		cv2.destroyAllWindows()
		
		# initialize the camera and grab a reference to the raw camera capture
		self._camera = PiCamera()
		self._camera.resolution = (self.__cameraResolutionX, self.__cameraResolutionY)
		self._camera.framerate = 32
		self._rawCapture = PiRGBArray(self._camera) #, size=(self._camera.resolution.width, self._camera.resolution.height))
		
		# allow the camera to warmup
		time.sleep(0.1)
		
		cascade_fn =  "/home/pi/opencv-3.1.0/data/haarcascades/haarcascade_frontalface_alt.xml"
		nested_fn  =  "/home/pi/opencv-3.1.0/data/haarcascades/haarcascade_eye.xml"
		#cascade_fn = args.get('--cascade', "../../data/haarcascades/haarcascade_frontalface_default.xml")
		#nested_fn  = args.get('--nested-cascade', "../../data/haarcascades/haarcascade_eye.xml")
	
		self._cascade = cv2.CascadeClassifier(cascade_fn)
		self._nested = cv2.CascadeClassifier(nested_fn)
		
		for frame in self._camera.capture_continuous(self._rawCapture, format="bgr", use_video_port=True):

			if (super().updating_ended == True):
				return;
						
			# grab the raw NumPy array representing the image, then initialize the timestamp
			# and occupied/unoccupied text
			image = frame.array
			
			# local modules
			#from video import create_capture
			from common import clock, draw_str
			
			#self._camera.capture(self._rawCapture, format="bgr")
			#image = self._rawCapture.array
			
			cv2.imshow('image', image)
		 
			# clear the stream in preparation for the next frame
			self._rawCapture.truncate(0)
				
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			gray = cv2.equalizeHist(gray)

			t = clock()
			rects = self.detect(gray, self._cascade)
					
			if (self._showImage==True):
				vis = image.copy()
				self.draw_rects(vis, rects, (0, 255, 0))
				
			dt = 0
			
			found_something = False
			
			if not self._nested.empty():
				posX = -1
				posY = -1
				bestWidth = -1
				for x1, y1, x2, y2 in rects:
					width = x2-x1
					if (width > bestWidth):
						bestWidth = width
						posX = (x1+(x2-x1)/2) / self._camera.resolution.width
						posY = (y1+(y2-y1)/2) / self._camera.resolution.height
					if (self._showImage==True):
						roi = gray[y1:y2, x1:x2]
						vis_roi = vis[y1:y2, x1:x2]
						subrects = self.detect(roi.copy(), self._nested)
						self.draw_rects(vis_roi, subrects, (255, 0, 0))
				self.posXFace = posX
				self.posYFace = posY
				
				dt = clock() - t
				
				if (posX != -1):
					#print('camera time: %.1f ms' % (dt*1000))
					found_something = True
			
			if (self._showImage==True):
				draw_str(vis, (20, 20), 'time: %.1f ms' % (dt*1000))
				cv2.imshow('facedetect', vis)
				
			if (found_something == True):
				time.sleep(self._delay_seconds)
			else:
				time.sleep(self._delay_seconds_when_idle)
				

	def ResetFace(self):
		self.posXFace = -1
		self.posYFace = -1

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down camera")
			super().EndUpdating()

	def __del__(self):
			self.Release()

if __name__ == '__main__':
	
	testCamera = Camera();
	
	
	while (True):
		if (testCamera.posXFace != -1):
			print(str(testCamera.posXFace) + " / " + str(testCamera.posYFace))
			testCamera.ResetFace()
		time.sleep(0.01)
