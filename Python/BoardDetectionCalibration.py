#!/usr/bin/env python


#     ##############################
#     # GO stone board calibration #
#     ##############################
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
import numpy as np
from CameraStoneDetection import CameraStoneDetection

class BoardDetectionCalibration():

	_released					= False
	_cameraStoneDetection		= None;
	_averageSize				= 0;

	def __init__(self, cameraStoneDetection):
		self._cameraStoneDetection = cameraStoneDetection;
		self.Init();

	def Init(self):
		print("Init board detection calibaration")
		self._cameraStoneDetection.Update(); # warm up camera
		
	def Calibrate(self):
		# need to find 4 black stones in the corners and one white in the center
		for i in range(0,1):
			self._cameraStoneDetection.Update();
			white = self._cameraStoneDetection.RectsWhite
			black = self._cameraStoneDetection.RectsBlack
			blackAndWhite = np.concatenate((white, black), 0)
			
			# find average size
			sizeCount = 0;
			for x, y, b, h in blackAndWhite:
				sizeCount += b + h;
				
			averageSize = sizeCount / (len(blackAndWhite) * 2);
			
			# filter out stones not matching to average size
			tolerance = 0.25;
			stones = [];
			for x, y, b, h in blackAndWhite:
				factor1 = b / averageSize
				factor2 = h / averageSize
				if (factor1 < 1+tolerance and factor1 > 1-tolerance and factor2 < 1+tolerance and factor2 > 1-tolerance):
					# stone size is in tolerance
					stones.extend([[x,y,b,h]])
					
			if (len(stones)==5):
				# well done - we have found the 4 black and the 1 white stone
				self._averageSize = averageSize;

			#print(len(stones))
				
			
			time.sleep(1);
			
	#def Update(self):
	#	
	#	return

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down board detection calibaration")

	def __del__(self):
			self.Release()

if __name__ == '__main__':
	
	camera = CameraStoneDetection();
	boardDetCalib = BoardDetectionCalibration(camera);

	for c in range(0,30):
		boardDetCalib.Calibrate();
		time.sleep(0.1)
