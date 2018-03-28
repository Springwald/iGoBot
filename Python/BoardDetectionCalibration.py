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
from CameraStoneDetection import CameraStoneDetection

class BoardDetectionCalibration():

	_released					= False
	_cameraStoneDetection		= None;

	def __init__(self, cameraStoneDetection):
		self._cameraStoneDetection = cameraStoneDetection;
		self.Init();

	def Init(self):
		print("Init BoardDetectionCalibration")
			
	def Update(self):
		self._cameraStoneDetection.Update();
		return

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down camera")

	def __del__(self):
			self.Release()

if __name__ == '__main__':
	
	camera = CameraStoneDetection();
	boardDetCalib = BoardDetectionCalibration(camera);

	for c in range(0,30):
		boardDetCalib.Update();
		time.sleep(0.1)
