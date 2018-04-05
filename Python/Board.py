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
	
	Empty						= 0;
	Black						= 1;
	White						= 2;
	
	_boardSize					= 0; # 9, 13, 19
	_fields						= [];
	
	# Stepper motor positions
	_13x13_xMin						= 735; 
	_13x13_xMax						= 3350;
	_13x13_yMin						= 100; 
	_13x13_yMax						= 2890;
	
	_9x9_xMin						= 1120; 
	_9x9_xMax						= 2940;
	_9x9_yMin						= 560; 
	_9x9_yMax						= 2400;
	
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
			if (boardSize == 9):
				print("Board: size " , boardSize, "x", boardSize);
				self.StepperMinX = self._9x9_xMin;
				self.StepperMaxX = self._9x9_xMax
				self.StepperMinY = self._9x9_yMin;
				self.StepperMaxY = self._9x9_yMax;
			else:
				throw ("unknown board size " , boardSize, "x", boardSize);
		
		# init board dimensions with 0 values (0=empty, 1=black, 2= white)
		self._fields =  [[0 for i in range(boardSize)] for j in range(boardSize)]
		
	# converts x=1,y=2 to A1
	def XyToAz(self, x,y):
		return chr(65+x)+str(y+1);
		
	# converts A1 to [0,0]
	def AzToXy(self, azNotation):
		if (len(azNotation) != 2):
			print ("board.AzToXy for '" + azNotation + "' is not exact 2 chars long");
			return None;
		return [ord(azNotation[0])-65, int(azNotation[1])-1]
		
	def GetField(self,x,y):
		return self._fields[x][y];
		
	def SetField(self,x,y, value):
		self._fields[x][y] = value;
		
	def GetNewBlackStones(self, detectedBlackStones):
	# what are the new black stones in the list, not still on the board?
		newBlack = [];
		for stone in detectedBlackStones:
			print ("checking field ",stone[0] ,stone[1], self.GetField(stone[0],stone[1]));
			if (self.GetField(stone[0],stone[1]) == self.Black):
				# no new black stone
				print("black stone on ",stone[0] ,stone[1], "already existed.");
			else:
				print("adding ",stone[0] ,stone[1],"to new black stone result");
				newBlack.extend([[stone[0],stone[1]]])
		return newBlack;

	def GetStepperXPos(self, fieldX):
		return self.StepperMinX + int(fieldX * 1.0 * ((self.StepperMaxX-self.StepperMinX) / (self._boardSize-1.0)));
		
	def GetStepperYPos(self, fieldY):
		return self.StepperMinY + int(fieldY * 1.0 * ((self.StepperMaxY-self.StepperMinY) / (self._boardSize-1.0)));
		
if __name__ == '__main__':
	
	board  = Board(13)
	print (board._fields)
	print (board.AzToXy("A1"))
	board.SetField(0,0,board.Black);
	print(board.GetField(0,0));
	print(board.GetField(0,0) == board.Black);
	
	
