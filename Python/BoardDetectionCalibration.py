#!/usr/bin/env python

#     iGoBot - a GO game playing robot
#
#     ##############################
#     # GO stone board calibration #
#     ##############################
#
#     Project website: http://www.springwald.de/hi/igobot
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
	
	_boardSize					= 0; # 9, 13, 19
	
	_cameraStoneDetection		= None;
	_averageSize				= 0;
	_averageCenter 				= None;
	
	_calTopLeft 				= None; 
	_calTopRight 				= None;
	_calBottomRight				= None;
	_calBottomLeft 				= None;
	
	BlackStoneCoords = []; # [[x,y],[x,y]...]
	WhiteStoneCoords = []; # [[x,y],[x,y]...]
	
	def __init__(self, cameraStoneDetection, boardSize):
		self._boardSize = boardSize;
		self._cameraStoneDetection = cameraStoneDetection;
		self.Init();
		
	def IsCalibrated(self):
		return self._averageSize != 0;

	def Init(self):
		print("Init board detection calibaration for board size " + str(self._boardSize) + "x" + str(self._boardSize))
		self._cameraStoneDetection.Update(); # warm up camera
		
	def Update(self):
		self._cameraStoneDetection.Update();
		if (self.IsCalibrated() == False):
			print("BoardDetectionCalibration.Update: not calibrated yet");
			self.BlackStoneCoords = [];
			self.WhiteStoneCoords = [];
			return;
		
		blackStones = self.FilterToTolerance(self._cameraStoneDetection.RectsBlack, self._averageSize);
		blackCenters = self.StonesToCenters(blackStones);
		self.BlackStoneCoords = self.GetBoardKoordinates(blackCenters);
		
		whiteStones = self.FilterToTolerance(self._cameraStoneDetection.RectsWhite, self._averageSize);
		whiteCenters = self.StonesToCenters(whiteStones);
		self.WhiteStoneCoords = self.GetBoardKoordinates(whiteCenters);
		
	def GetBoardKoordinates(self, centers):
		if (centers == None):
			return [];
		if (len(centers)==0):
			return [];
		onlyInsideBoard = self.GetOnlyCentersInsideBoard(centers);
		#print ("GetBoardKoordinates| all:" + str(len(centers)) + " > inside board:"  +str(len(onlyInsideBoard)));
		return onlyInsideBoard
		
	def ToBoardFields(self, centerPoints):
		result = [];
		for cX, cY in centerPoints:
			y = 0;
			if (cX < self._averageCenter[0]): # left side of the board
				boardHeight = self._calBottomLeft[1] - self._calTopLeft[1];
				y =  (cY - self._calTopLeft[1]) / boardHeight * (self._boardSize-1);
			else: # right side of the board
				boardHeight = self._calBottomRight[1] - self._calTopRight[1];
				y = (cY - self._calTopRight[1]) / boardHeight * (self._boardSize-1);
				
			x = 0;
			if (cY < self._averageCenter[1]): # top side of the board
				boardWidth = self._calTopRight[0] - self._calTopLeft[0];
				x = (cX - self._calTopLeft[0]) / boardWidth * (self._boardSize-1);
			else: # bottom side of the board
				boardWidth = self._calBottomRight[0] - self._calBottomLeft[0];
				x = (cX - self._calBottomLeft[0]) / boardWidth * (self._boardSize-1);
			result.extend([[int(round(x)),int(round(y))]])
			
		#print (result);
		return result

	# converts x=1,y=2 to A1
	def FieldToAZNotation(self, x,y):
		return chr(65+x)+str(y+1);
		
	def FieldsToAZNotation(self, fields):
		result = [];
		#print (fields);
		for x, y in fields:
			result.extend([self.FieldToAZNotation(x,y)])	
		return result;
	
	def GetOnlyCentersInsideBoard(self, centers):
		resultStones = [];
		tolerance = self._averageSize / 2;
		for x, y in centers:
			if (x + tolerance < min(self._calBottomLeft[0], self._calTopLeft[0])):
				continue
			if (x - tolerance > min(self._calBottomRight[0], self._calTopRight[0])):
				continue
			if (y + tolerance < min(self._calTopLeft[1], self._calTopRight[1])):
				continue
			if (y - tolerance > min(self._calBottomRight[1], self._calBottomLeft[1])):
				continue
			resultStones.extend([[x,y]])
		return resultStones;

	def Calibrate(self):
		self.DeleteCalibration();
		# need to find 4 black stones in the corners and one white in the center
		self._cameraStoneDetection.Update();
		white = self._cameraStoneDetection.RectsWhite
		black = self._cameraStoneDetection.RectsBlack

		if (len(white) >= 1 and len(black)>=4):
			blackAndWhite = np.concatenate((white, black), 0)
			
			if (len(blackAndWhite) > 0):
				averageSize = self.GetAverageSize(blackAndWhite);
				
				# filter out stones not matching to average size
				whiteStones = self.FilterToTolerance(white, averageSize);
				blackStones = self.FilterToTolerance(black, averageSize);
						
				if (len(whiteStones)==1 and len(blackStones)==4):
					# well done - we have found the 4 black and the 1 white stone
					print("found the 4+1 calibration stones");
					
					if (len(blackAndWhite) == 5):
						self._averageSize = averageSize;
					else:
						# calculate the averageSize for only the 5 correct stones (
						print("recalculating average size without wrong stones");
						allGoodStones = np.concatenate((whiteStones, blackStones), 0)
						self._averageSize = self.GetAverageSize(allGoodStones);
					
					# now find the 4 black corner stones
					blackCenters = self.StonesToCenters(blackStones);
					averageCenter = self.FindAverageCenter(blackCenters);
					self._averageCenter = averageCenter;
					
					# define the 4 calibration points
					for x, y in blackCenters:
						if (x < averageCenter[0]):
							if (y < averageCenter[1]):
								self._calTopLeft = [x,y]
							else:
								self._calBottomLeft = [x,y]
						else:
							if (y < averageCenter[1]):
								self._calTopRight = [x,y]
							else:
								self._calBottomRight = [x,y]
								
					if (self._calTopLeft == None):
						print("Calibration failed:  _calTopLeft missing!");
						self.DeleteCalibration();
						return;
						
					if (self._calBottomLeft == None):
						print("Calibration failed:  _calBottomLeft missing!");
						self.DeleteCalibration();
						return;
						
					if (self._calBottomRight == None):
						print("Calibration failed:  _calBottomRight missing!");
						self.DeleteCalibration();
						return;
						
					if (self._calTopRight == None):
						print("Calibration failed:  _calTopRight missing!");
						self.DeleteCalibration();
						return;
					
					print("board calibration successfull!")

	def DeleteCalibration(self):
		self._calTopLeft 		= None; 
		self._calTopRight 		= None;
		self._calBottomRight	= None;
		self._calBottomLeft 	= None;
		self._averageSize 		= 0;
		self._averageCenter		= None;
						
	def FindAverageCenter(self, centerPoints):
		minX =  100000;
		maxX = -100000;
		minY =  100000;
		maxY = -100000;
		for x, y in centerPoints:
			minX = min(minX, x);
			minY = min(minY, x);
			maxX = max(maxX, x);
			maxY = max(maxY, x);
		return [minX + (maxX - minX) / 2, minY + (maxY - minY) / 2]
		
	# converts [[x,y,b,h]] to [[x,y]]	
	def StonesToCenters(self, stones):
		result = [];
		for x, y, b, h in stones:
			result.extend([[x+b/2, y+h/2]])
		return result;
			
	def FilterToTolerance(self, stones, averageSize):
		tolerance = 0.25;
		resultStones = [];
		for x, y, b, h in stones:
			factor1 = b / averageSize
			factor2 = h / averageSize
			if (factor1 < 1+tolerance and factor1 > 1-tolerance and factor2 < 1+tolerance and factor2 > 1-tolerance):
				# stone size is in tolerance
				resultStones.extend([[x,y,b,h]])
		return resultStones;
		
	def GetAverageSize(self, stones):
		if (len(stones) > 0):
			# find average size
			sizeCount = 0;
			for x, y, b, h in stones:
				sizeCount += b + h;
			return sizeCount / (len(stones) * 2);
		else:
			return 0;

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down board detection calibaration")

	def __del__(self):
			self.Release()

if __name__ == '__main__':
	
	camera = CameraStoneDetection();
	boardDetCalib = BoardDetectionCalibration(camera, boardSize=13);

	#time.sleep(4)

	while(True):
		if (boardDetCalib.IsCalibrated()==True):
			boardDetCalib.Update();
			blackCoords = boardDetCalib.BlackStoneCoords;
			#print (blackCoords);
			blackFields= boardDetCalib.ToBoardFields(blackCoords);
			#print (blackFields);
			blackAZ = boardDetCalib.FieldsToAZNotation(blackFields);
			print (blackAZ);
		else:
			boardDetCalib.Calibrate();
		#time.sleep(0.1)
