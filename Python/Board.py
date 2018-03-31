#!/usr/bin/env python

#     iGoBot - a GO game playing robot
#
#     ##############################
#     # GO stone board coordinates #
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


class Board():

	_released					= False
	
	_boardSize					= 0; # 9, 13, 19
	_fields						= [];
	
	# Stepper motor positions
	_13x13_xMin						= 735; #735;
	_13x13_xMax						= 3350;
	_13x13_yMin						= 100; # 90;
	_13x13_yMax						= 2840;
	
	StepperMinX						= 0;
	StepperMaxX 					= 0;
	StepperMinY						= 0;
	StepperMaxY						= 0;
	
	def __init__(self, boardSize):
		self._boardSize = boardSize;
		
		if (boardSize == 13):
			print("Board: size " , boardSize, "x", boardSize);
			self.StepperMinX = self._13x13_xMin;
			self.StepperMaxX = self._13x13_xMax
			self.StepperMinY = self._13x13_yMin;
			self.StepperMaxY = self._13x13_yMax;
		else:
			throw ("unknown board size " , boardSize, "x", boardSize);
		
		# init board dimensions with 0 values (0=empty, 1=black, 2= white)
		self._fields =  [[0 for i in range(boardSize)] for j in range(boardSize)]

	def GetStepperXPos(self, fieldX):
		return self.StepperMinX + int(fieldX * 1.0 * ((self.StepperMaxX-self.StepperMinX) / (self._boardSize-1.0)));
		
	def GetStepperYPos(self, fieldY):
		return self.StepperMinY + int(fieldY * 1.0 * ((self.StepperMaxY-self.StepperMinY) / (self._boardSize-1.0)));
		
if __name__ == '__main__':
	
	board  = Board(13)
	print (board._fields);

	
