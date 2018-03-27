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
import grovepi

from hardware.PCF8574 import PCF8574
from hardware.I2cIoExpanderPcf8574Synchron import I2cIoExpanderPcf8574Synchron
from hardware.StepperMotorControlSynchron import StepperMotorControlSynchron
from hardware.Gripper import Gripper
from hardware.Light import Light

import atexit

class iGoBot:

	I2cIoExpanderPcf8574Adress		= 0x3e
	_xAxisAdress					= 0x0d
	_yAxisAdress					= 0x0e
	_zAxisAdress					= 0x0f
	_gripperAdress					= 0x40
	_lightGrovePort					= 8
	
	_ended							= False
	_released						= False
	
	_xAxis 							= None;
	_yAxis 							= None;
	_zAxis 							= None;
	_light							= None;
	_gripper 						= None;
	
	_zPosUp							= 600;
	_zPosOnBoard					= 720;
	
	_13x13_xMin						= 735;
	_13x13_xMax						= 3350;
	_13x13_yMin						= 90;
	_13x13_yMax						= 2900;
	

	def __init__(self):
		#pygame.init()
		#pygame.mixer.quit() # to prevent conflicts with speech output (audio device busy)
		#screenInfo = pygame.display.Info()
		#if (screenInfo.current_w > 900):
		#self.lcd = pygame.display.set_mode((800,480))
		#else:
		#	self.lcd = pygame.display.set_mode((800,480), FULLSCREEN, 16)
		
		endStop = I2cIoExpanderPcf8574Synchron(0x3e, useAsInputs=True)
		self._zAxis = StepperMotorControlSynchron("z-axis", self._zAxisAdress, 940,   endStop,  64, [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001])
		self._xAxis = StepperMotorControlSynchron("x-axis", self._xAxisAdress, 4100,  endStop,  32, [0b0001, 0b0101, 0b0100, 0b0110, 0b0010, 0b1010, 0b1000, 0b1001])
		self._yAxis = StepperMotorControlSynchron("y-axis", self._yAxisAdress, 3800,  endStop, 128, [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001])
		self.WaitForAllMotors();
		
		return 
		self.MoveToXY(self._13x13_xMax,self._13x13_yMax);
		self.MoveToZ(self._zPosOnBoard);
		time.sleep(10);
		
		self._gripper = Gripper(i2cAdress=self._gripperAdress, busnum=1)
		self._gripper.openGripper();
		
		self._light = Light(self._lightGrovePort);
		self._light.On();
		
		self.MoveToXY(self._13x13_xMin + (self._13x13_xMax - self._13x13_xMin) / 2, self._13x13_yMin + (self._13x13_yMax - self._13x13_yMin) / 2);
		self.TakeStoneFromBoard();
		
		self.MoveToXY(self._13x13_xMin, self._13x13_yMin);
		self.PutStoneToBoard();
		self.TakeStoneFromBoard();
		
		self.MoveToXY(self._13x13_xMax, self._13x13_yMax);
		self.PutStoneToBoard();
		self.TakeStoneFromBoard();
		
		self.MoveToXY(self._13x13_xMin + (self._13x13_xMax - self._13x13_xMin) / 2, self._13x13_yMin + (self._13x13_yMax - self._13x13_yMin) / 2);
		self.PutStoneToBoard();

	def TakeStoneFromBoard(self):
		self.MoveToZ(self._zPosUp);
		self.OpenGripper();
		self.MoveToZ(self._zPosOnBoard);
		self._gripper.closeGripper();
		self.CloseGripper();
		self.MoveToZ(self._zPosUp);
		return;
		
	def PutStoneToBoard(self):
		self.MoveToZ(self._zPosOnBoard);
		self.OpenGripper();
		self.MoveToZ(self._zPosUp);
		return;
		
	def OpenGripper(self):
		self._gripper.openGripper();
		while(self._gripper.allTargetsReached == False):
			self._gripper.Update();
			self.UpdateMotors();
			
	def CloseGripper(self):
		self._gripper.closeGripper();
		while(self._gripper.allTargetsReached == False):
			self._gripper.Update();
			self.UpdateMotors();
	
	# To give the motors the chance to go to sleep
	def UpdateMotors(self):
		self._xAxis.Update();
		self._yAxis.Update();
		self._zAxis.Update();
		
	def WaitForAllMotors(self):
		while(self._zAxis.targetReached==False):
			self.UpdateMotors();
		while(self._xAxis.targetReached==False):
			self.UpdateMotors();
		while(self._yAxis.targetReached==False):
			self.UpdateMotors();

	def MoveToXY(self, posX, posY):	
		self.MoveToX(posX);
		self.MoveToY(posY);

	def MoveToX(self, pos):
		self._xAxis.targetPos = pos;
		self.WaitForAllMotors();
			
	def MoveToY(self, pos):
		self._yAxis.targetPos = pos;
		self.WaitForAllMotors();
		
	def MoveToZ(self, pos):
		self._zAxis.targetPos = pos;
		self.WaitForAllMotors();

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down iGoBot")
			
			if (self._gripper != None):
				self._gripper.openGripper();
				while(self._gripper.allTargetsReached == False):
					self._gripper.Update();
				self._gripper.Release();
			
			if (self._zAxis != None):
				self.MoveToZ(0);
				self._zAxis.Release()
			
			if (self._xAxis != None):
				self.MoveToX(0);
				self._xAxis.Release()

			if (self._yAxis != None):
				self.MoveToY(0);
				self._yAxis.Release()
				
			if (self._light != None):
				self._light.Off();

			self._ended = True

	def __del__(self):
		self.Release()
		
def exit_handler():
	bot.Release()

if __name__ == "__main__":
	
	bot = iGoBot()
	
	atexit.register(exit_handler)
	
	ended = False;
	
	while ended == True:
		
		time.sleep(1)
		
		bot.UpdateMotors();
		
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
					


        
        
        
        

    





