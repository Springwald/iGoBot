#!/usr/bin/env python

#     ###############################
#     # iGoBot - a GO playing robot #
#     ###############################
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
from os.path import abspath

import time
from random import randrange, uniform
import math
import pygame

from hardware.PCF8574 import PCF8574
from hardware.I2cIoExpanderPcf8574Synchron import I2cIoExpanderPcf8574Synchron
from hardware.StepperMotorControlSynchron import StepperMotorControlSynchron
from hardware.Gripper import Gripper

import atexit

class iGoBot:

	I2cIoExpanderPcf8574Adress		= 0x3e
	_xAxisAdress					= 0x0d
	_yAxisAdress					= 0x0e
	_zAxisAdress					= 0x0f
	_gripperAdress					= 0x40
	
	_ended							= False
	_released						= False
	
	_xAxis 							= None;
	_yAxis 							= None;
	_zAxis 							= None;
	_gripper 						= None;
	
	_zPosUp							= 100;
	_zPosOnBoard					= 695;
	
	_9x9_xMin						= 730;
	_9x9_xMax						= 3350;
	_9x9_yMin						= 90;
	_9x9_yMax						= 2850;
	

	def __init__(self):
		pygame.init()
		pygame.mixer.quit() # to prevent conflicts with speech output (audio device busy)
		screenInfo = pygame.display.Info()
		#if (screenInfo.current_w > 900):
		self.lcd = pygame.display.set_mode((800,480))
		#else:
		#	self.lcd = pygame.display.set_mode((800,480), FULLSCREEN, 16)
		
		endStop = I2cIoExpanderPcf8574Synchron(0x3e, useAsInputs=True)
		self._zAxis = StepperMotorControlSynchron("z-axis", self._zAxisAdress, 940,   endStop,  64, [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001])
		self._xAxis = StepperMotorControlSynchron("x-axis", self._xAxisAdress, 4100,  endStop,  32, [0b0001, 0b0101, 0b0100, 0b0110, 0b0010, 0b1010, 0b1000, 0b1001])
		self._yAxis = StepperMotorControlSynchron("y-axis", self._yAxisAdress, 3800,  endStop, 128, [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001])
		
		self._gripper = Gripper(i2cAdress=self._gripperAdress, busnum=1)
		self._gripper.openGripper();
		
		self.MoveToXY(self._9x9_xMin, self._9x9_yMin);
		self.TakeStoneFromBoard();
		self.MoveToXY(self._9x9_xMax, self._9x9_yMax);
		self.PutStoneToBoard();
		
		self.TakeStoneFromBoard();
		self.MoveToXY(self._9x9_xMin + (self._9x9_xMax - self._9x9_xMin) / 2, self._9x9_yMin + (self._9x9_yMax - self._9x9_yMin) / 2);
		self.PutStoneToBoard();

	def TakeStoneFromBoard(self):
		self._zAxis.MoveToPosAndWait(self._zPosUp);
		self._gripper.openGripper();
		while(self._gripper.allTargetsReached == False):
			time.sleep(0.4);
		self._zAxis.MoveToPosAndWait(self._zPosOnBoard);
		self._gripper.closeGripper();
		while(self._gripper.allTargetsReached == False):
			time.sleep(0.4);
		self._zAxis.MoveToPosAndWait(self._zPosUp);
		return;
		
	def PutStoneToBoard(self):
		self._zAxis.MoveToPosAndWait(self._zPosOnBoard);
		self._gripper.openGripper();
		while(self._gripper.allTargetsReached == False):
			time.sleep(0.4);
		self._zAxis.MoveToPosAndWait(self._zPosUp);
		return;

	def MoveToXY(self, xPos, yPos):
		self._xAxis.MoveToPosAndWait(xPos);
		self._yAxis.MoveToPosAndWait(yPos);
		
	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down iGoBot")
			
			if (self._gripper != None):
				self._gripper.openGripper();
				while(self._gripper.allTargetsReached == False):
					time.sleep(0.4);
				self._gripper.Release();
			
			if (self._zAxis != None):
				self._zAxis.Release()
			
			if (self._xAxis != None):
				self._xAxis.Release()

			if (self._yAxis != None):
				self._yAxis.Release()

			self._ended = True

	def __del__(self):
		self.Release()
		
def exit_handler():
	bot.Release()

if __name__ == "__main__":
	
	bot = iGoBot()
	
	ended = False;
	
	while ended == False:
		
		time.sleep(0.5)
		
		#roobert.Update()
		
		#roobert.RotateDemoForPhoto();
		
		#roobert.RandomHeadMovement()
		
		#roobert.FollowFace()
		#roobert.drive_avoiding_obstacles()

		events = pygame.event.get()
	
		for event in events:
			if event.type == pygame.MOUSEBUTTONUP:
				ended = True 
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					ended = True 
				if event.key == pygame.K_TAB:
					#roobert.Greet()
					#start_new_thread(roobert.Greet,())
					a=0

        
        
        
        

    





