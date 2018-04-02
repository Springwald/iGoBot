#!/usr/bin/env python

#     iGoBot - a GO game playing robot
#      _ _____      ______       _   
#     (_)  __ \     | ___ \     | |  
#      _| |  \/ ___ | |_/ / ___ | |_ 
#     | | | __ / _ \| ___ \/ _ \| __|
#     | | |_\ \ (_) | |_/ / (_) | |_ 
#     |_|\____/\___/\____/ \___/ \__|
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
from os.path import abspath

import time
from random import randrange, uniform
import math
import pygame
import grovepi

from Board import Board
from CameraStoneDetection import CameraStoneDetection
from BoardDetectionCalibration import BoardDetectionCalibration
from SpeechOutput import SpeechOutput

from hardware.PCF8574 import PCF8574
from hardware.I2cIoExpanderPcf8574Synchron import I2cIoExpanderPcf8574Synchron
from hardware.StepperMotorControlSynchron import StepperMotorControlSynchron
from hardware.GripperAndDispenser import GripperAndDispenser
from hardware.Light import Light
from hardware.RgbLeds import RgbLeds

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
	_leds							= None;
	_gripperAndDispenser			= None;
	_speech							= None;
	_board							= None;
	_switches 						= None;
	
	_camera							= None;
	_cameraStoneDetection			= None;
	
	# where to move to drop the stone into the drop storage
	_xPosStoneStorageDrop			= 4400
	_yPosStoneStorageDrop			= 3800
	
	# where to move to grab a new stone from dispenser
	_xPosStoneStorageGrab			= 4160 ##
	_yPosStoneStorageGrab			= 3470
	
	_yPosOutOfCameraSight			= 3800
	
	_zPosMaxUp						= 0;
	_zPosUp							= 400;
	_zPosDropOnBoard				= 570;
	_zPosOnBoard					= 630;
	_zPosOnDispenserGrab			= 700;
	
	def __init__(self, boardSize=13):
		#pygame.init()
		#pygame.mixer.quit() # to prevent conflicts with speech output (audio device busy)
		#screenInfo = pygame.display.Info()
		#if (screenInfo.current_w > 900):
		#self.lcd = pygame.display.set_mode((800,480))
		#else:
		#	self.lcd = pygame.display.set_mode((800,480), FULLSCREEN, 16)
		
		self._light = Light(self._lightGrovePort);
		self._light.On();
		
		self._leds = RgbLeds();
		
		self._speech = SpeechOutput();
		
		self._camera = CameraStoneDetection();
		self._board = Board(boardSize);
		
		self._gripperAndDispenser = GripperAndDispenser(i2cAdress=self._gripperAdress, busnum=1)
		self._gripperAndDispenser.openGripper();
		
		endStop = I2cIoExpanderPcf8574Synchron(0x3e, useAsInputs=True)
		self._switches = endStop;
		self._zAxis = StepperMotorControlSynchron("z-axis", self._zAxisAdress, 940,   endStop,  64, [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001], rampSafeArea=20)
		self._xAxis = StepperMotorControlSynchron("x-axis", self._xAxisAdress, 4400,  endStop,  32, [0b0001, 0b0101, 0b0100, 0b0110, 0b0010, 0b1010, 0b1000, 0b1001])
		self._yAxis = StepperMotorControlSynchron("y-axis", self._yAxisAdress, 3800,  endStop, 128, [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001])
		self.WaitForAllMotors();
		
		self.MoveToZ(self._zPosUp);
		
		# move to stone storage drop
		if (False):
			self.DropStoneInStorage();
			time.sleep(30);
		
		# test stone board coordinates
		if (False):
			for i in [[0,0],[0,12],[12,12],[12,0]]:
				self.MoveToXY(self._board.GetStepperXPos(i[0]),self._board.GetStepperYPos(i[1]));
				for a in range(0,3):
					self.TakeStoneFromBoard();
					self.PutStoneToBoard();
					time.sleep(1);
			
		# take stone from 0, 0 and drop it into storage
		if (False):
			self.MoveToXY(self._board.GetStepperXPos(0), self._board.GetStepperYPos(0));
			self.TakeStoneFromBoard();
			self.DropStoneInStorage();
			
		self.MoveOutOfCameraSight();
		
		# calibrate camera with 4 black and 1 white stones
		self._cameraStoneDetection = BoardDetectionCalibration(self._camera, boardSize);
		while(self._cameraStoneDetection.IsCalibrated()==False):
			self._cameraStoneDetection.Calibrate();
		return;
		
	

	def TakeStoneFromBoard(self):
		self.MoveToZ(self._zPosUp);
		self.OpenGripper();
		self.MoveToZ(self._zPosOnBoard);
		self.CloseGripper();
		self.MoveToZ(self._zPosUp);
		return;
		
	def PutStoneToBoard(self):
		self.MoveToZ(self._zPosDropOnBoard);
		self.OpenGripper();
		self.MoveToZ(self._zPosUp);
		return;
		
	def DropStoneInStorage(self):
		self.MoveToZ(self._zPosMaxUp);
		self.MoveToXY(self._xPosStoneStorageDrop, self._yPosStoneStorageDrop);
		self.OpenGripper();
		
	def GrabStoneFromStorage(self):
		self.MoveToZ(self._zPosMaxUp); # z max up
		self.MoveToXY(self._xPosStoneStorageGrab, self._yPosStoneStorageGrab); # go to storage grab zone
		self._gripperAndDispenser.dispenserGrab();
		for a in range(0,3):
			# shuffle stone into dispenser hole
			self._gripperAndDispenser.dispenserGrab();
			while(self._gripperAndDispenser.allTargetsReached == False):
				self._gripperAndDispenser.Update();
				self.UpdateMotors();
			self._gripperAndDispenser.dispenserGive();
			while(self._gripperAndDispenser.allTargetsReached == False):
				self._gripperAndDispenser.Update();
				self.UpdateMotors();
		self.MoveToZ(self._zPosOnDispenserGrab);
		self.CloseGripper();
		self.MoveToZ(self._zPosMaxUp);
		
	def OpenGripper(self):
		self._gripperAndDispenser.openGripper();
		while(self._gripperAndDispenser.allTargetsReached == False):
			self._gripperAndDispenser.Update();
			self.UpdateMotors();
			
	def CloseGripper(self):
		self._gripperAndDispenser.closeGripper();
		while(self._gripperAndDispenser.allTargetsReached == False):
			self._gripperAndDispenser.Update();
			self.UpdateMotors();
	
	# To give the motors the chance to go to sleep
	def UpdateMotors(self):
		self._xAxis.Update();
		self._yAxis.Update();
		self._zAxis.Update();
		
	def WaitForAllMotors(self):
		while(self._gripperAndDispenser.allTargetsReached==False):
			self._gripperAndDispenser.Update();
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
		
	def MoveOutOfCameraSight(self):
		self.MoveToZ(self._zPosMaxUp);
		self.MoveToY(self._yPosOutOfCameraSight);
		
	def TakeStoneFromPosition(self,x,y):
		self._MoveToXY(x,y);
		self.TakeStoneFromBoard();
		
	def PutStoneToFieldPos(self, fieldX, fieldY):
		stepperX = self._board.GetStepperXPos(fieldX);
		stepperY = self._board.GetStepperYPos(fieldY);
		self.MoveToXY(stepperX, stepperY);
		self.PutStoneToBoard();
		
	def Speak(self, sentence, wait=False):
		bot._speech.Speak(sentence, wait);

	def StoreAllWhiteStones(self):
		tries = 0;
		while (tries < 5):
			tries = tries + 1;
			
			# move arm out of camera sight
			self.MoveOutOfCameraSight();
		
			# check camera detection of white stones
			self.UpdateMotors();
			self._cameraStoneDetection.Update();
			whiteStonesCoords = self._cameraStoneDetection.WhiteStoneCoords;
			whiteStones = self._cameraStoneDetection.ToBoardFields(whiteStonesCoords)
			if (len(whiteStones) > 0):
				# there are still white stones
				tries = 0;
				# move to first white stone
				stone = whiteStones[0];
				print("found white stone on ", self._cameraStoneDetection.FieldToAZNotation(stone[0],stone[1]));
				stepperX = self._board.GetStepperXPos(stone[0]);
				stepperY = self._board.GetStepperYPos(stone[1]);
				self.MoveToXY(stepperX, stepperY);
				# take white stone
				self.TakeStoneFromBoard();
				# drop stone into storage
				self.DropStoneInStorage();
			else:
				# no more white stones
				print("no white stone detected, try ", tries);
				self.UpdateMotors();
				time.sleep(1);
			
	def WaitTillButtonPressed(self, color="green"):
		pressed = False;
		while(pressed == False):
			self.UpdateMotors();
			self._gripperAndDispenser.Update();
			self._leds.AnimateButtonGreen();
			if (self._switches.getBit(bit=16)):
				pressed = True;
		self._leds.clearButton();

	def PlayWhiteGame(self):
		self.Speak("Bitte lege Deine schwarzen Vorgabe Steine auf das Brett. Drücke dann die Taste.", wait=False);
		self.WaitTillButtonPressed(color="green");

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down iGoBot")
			
			if (self._cameraStoneDetection != None):
				self._cameraStoneDetection.Release();
				
			if (self._camera != None):
				self._camera.Release();
			
			if (self._gripperAndDispenser != None):
				self._gripperAndDispenser.openGripper();
				while(self._gripperAndDispenser.allTargetsReached == False):
					self._gripperAndDispenser.Update();
				self._gripperAndDispenser.Release();
			
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
				self._light.Release();
				
			if (self._leds != None):
				self._leds.Release();
				
			if (self._speech != None):
				self._speech.Release();

			self._ended = True

	def __del__(self):
		self.Release()
		
def exit_handler():
	bot.Release()

if __name__ == "__main__":
	
	bot = iGoBot()
	
	atexit.register(exit_handler)
	
	bot.PlayWhiteGame();
	
	if (False):
		bot._speech.Speak("Hallo")
		while (bot._speech.speaking==True):
				time.sleep(1)
		bot._speech.Speak("Möchtest Du eine Partie go mit mir spielen?");
		while (bot._speech.speaking==True):
				time.sleep(1)
		bot._speech.Speak("Ich habe eine Spielstärke von etwa 5 kyu.")
		while (bot._speech.speaking==True):
				time.sleep(1)
		
		for i in range(1,6):
			bot.GrabStoneFromStorage();
			bot.PutStoneToFieldPos(i,i);

		bot.StoreAllWhiteStones();
	
	
	
	
	#ended = False;
	
	#while ended == True:
		
		#time.sleep(1)
		
		#bot.UpdateMotors();
		
		#events = pygame.event.get()
	
		#for event in events:
			#if event.type == pygame.MOUSEBUTTONUP:
				#ended = True 
			#if event.type == pygame.KEYDOWN:
				#if event.key == pygame.K_ESCAPE:
					#ended = True 
				#if event.key == pygame.K_TAB:
					##roobert.Greet()
					##start_new_thread(roobert.Greet,())
					#a=0
					


        
        
        
        

    





