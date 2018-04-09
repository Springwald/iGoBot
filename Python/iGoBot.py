#!/usr/bin/python
#-*-coding:utf-8-*-
#vim: set enc=utf8:

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
import random

from Board import Board
from GnuGoRemote import GnuGoRemote
from CameraStoneDetection import CameraStoneDetection
from BoardDetectionCalibration import BoardDetectionCalibration
from DanielsRasPiPythonLibs.speech.SpeechOutput import SpeechOutput

from DanielsRasPiPythonLibs.hardware.PCF8574 import PCF8574
from DanielsRasPiPythonLibs.hardware.I2cIoExpanderPcf8574Synchron import I2cIoExpanderPcf8574Synchron
from DanielsRasPiPythonLibs.hardware.RgbLeds import RgbLeds
from hardware.Light import Light
from hardware.Motors import Motors
from hardware.iGoBotRgbLeds import iGoBotRgbLeds

import atexit
import gettext

englishSpeech = True

if (englishSpeech == True):
	en = gettext.translation('iGoBot', localedir='locale', languages=['en'])
	en.install
	_ = en.gettext
else:
	_ = lambda s: s

class iGoBot:

	englishSpeech 					= True;

	I2cIoExpanderPcf8574Adress		= 0x3e

	_lightGrovePort					= 8
	_soundcard						="plughw:1"
	
	_ended							= False
	_released						= False
	
	_motors							= None;
	_light							= None;
	_leds							= None;
	_speech							= None;
	_board							= None;
	_switches 						= None;
	
	_gnuGo							= None;
	
	_camera							= None;
	_cameraStoneDetection			= None;
	
	
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
		
		self._leds = iGoBotRgbLeds();
		
		self._speech = SpeechOutput(soundcard=self._soundcard, voice="-vmb-de2");
		
		self._camera = CameraStoneDetection();
		self._board = Board(boardSize);
		
		self._switches = I2cIoExpanderPcf8574Synchron(self.I2cIoExpanderPcf8574Adress, useAsInputs=True)
		
		self._motors = Motors(self._switches);
		
		self._gnuGo = GnuGoRemote(boardSize=boardSize)
		
		# move to stone storage drop
		if (False):
			self._motors.DropStoneInStorage();
			time.sleep(30);
		
		# test stone board coordinates
		if (False):
			#for i in [[0,0],[0,12],[12,12],[12,0]]:
			for i in [[0,0],[0,8],[8,8],[8,0]]:
				self._motors.MoveToXY(self._board.GetStepperXPos(i[0]),self._board.GetStepperYPos(i[1]));
				for a in range(0,3):
					self._motors.TakeStoneFromBoard();
					self._motors.PutStoneToBoard();
					time.sleep(1);
		
		# take stone from 0, 0 and drop it into storage
		if (False):
			self._motors.MoveToXY(self._board.GetStepperXPos(0), self._board.GetStepperYPos(0));
			self._motors.TakeStoneFromBoard();
			self._motors.DropStoneInStorage();
			
		self._motors.MoveOutOfCameraSight();
		
		# calibrate camera with 4 black and 1 white stones
		self._cameraStoneDetection = BoardDetectionCalibration(self._camera, boardSize);
		while(self._cameraStoneDetection.IsCalibrated()==False):
			self._cameraStoneDetection.Calibrate();
		return;

	def RemoveCapturedStoneFromBoard(self,x ,y):
		stepperX = self._board.GetStepperXPos(x);
		stepperY = self._board.GetStepperYPos(y);
		self._motors.MoveToXY(stepperX, stepperY);
		# take stone
		self._motors.TakeStoneFromBoard();
		# drop left or right from board
		if (self._board.GetField(x,y)== Board.Empty):
			self.Speak(_("Fehler! Ich wollte den Stein auf {x}/{y} entfernen, aber dort ist laut meiner Aufzeichnung gar kein Stein.").format(x=x,y=y));
			return;
		self._motors.DropCapturedStone(self._board.GetField(x,y) == Board.Black);
		self._board.SetField(x,y,Board.Empty);

	def PutStoneToFieldPos(self, fieldX, fieldY):
		stepperX = self._board.GetStepperXPos(fieldX);
		stepperY = self._board.GetStepperYPos(fieldY);
		self._motors.MoveToXY(stepperX, stepperY);
		self._motors.PutStoneToBoard();
		
	def UpdateFace(self):
		if (self._speech.IsSpeaking()):
			self._leds.Speak();
		else:
			self._leds.NeutralFace();
		
	def Speak(self, sentence, wait=False):
		print(">>>>>>" ,sentence);
		self._speech.Speak(sentence, wait=False);
		if (wait):
			while(self._speech.IsSpeaking()):
				self.UpdateFace();
				self._motors.UpdateMotors();
				self._motors.UpdateGripperAndDispenser();
				time.sleep(0.25);
			self.UpdateFace();

	def StoreAllWhiteStones(self):
		tries = 0;
		while (tries < 5):
			tries = tries + 1;
			
			# move arm out of camera sight
			self._motors.MoveOutOfCameraSight();
		
			# check camera detection of white stones
			self._motors.UpdateMotors();
			self._cameraStoneDetection.Update();
			whiteStones = self._cameraStoneDetection.WhiteStones
			if (len(whiteStones) > 0):
				# there are still white stones
				tries = 0;
				# move to first white stone
				stone = whiteStones[0];
				print("found white stone on {field}".format(field=self._cameraStoneDetection.FieldToAZNotation(stone[0],stone[1])));
				stepperX = self._board.GetStepperXPos(stone[0]);
				stepperY = self._board.GetStepperYPos(stone[1]);
				self._motors.MoveToXY(stepperX, stepperY);
				# take white stone
				self._motors.TakeStoneFromBoard();
				# drop stone into storage
				self._motors.DropStoneInStorage();
			else:
				# no more white stones
				print("no white stone detected, try {tries}".format(tries=tries));
				self._motors.UpdateMotors();
				time.sleep(1);
			
	def WaitTillButtonPressed(self, color="green"):
		pressed = False;
		self._motors.StandByAllMotors();
		# wait till pressed
		while(pressed == False):
			self._motors.UpdateGripperAndDispenser;
			self._leds.AnimateButtonGreen();
			self._leds.NeutralAndBlink();
			if (self._switches.getBit(bit=16)):
				pressed = True;
			self.UpdateFace();
		# wait till released
		while(pressed == True):
			self._motors.UpdateGripperAndDispenser;
			self._leds.AnimateButtonGreen();
			if (not self._switches.getBit(bit=16)):
				pressed = False;
		self.UpdateFace();
		self._leds.ClearButton();
		self._motors.WakeUpAllMotors();

	def GetNewStones(self, color=Board.Black):
		self._motors.MoveOutOfCameraSight();
		for i in range(1,2):
			self._cameraStoneDetection.Update();
		if (color==Board.Black):
			stones = self._cameraStoneDetection.BlackStones;
		else:
			stones = self._cameraStoneDetection.WhiteStones;
		newStones = self._board.GetNewStones(stones, color);
		return newStones;

	def ClearBoard(self):
		self._gnuGo.ClearBoard();
		self._board = Board(self._board._boardSize);
		
	def FindBestCameraSettings(self, ignoreStones=[]): # ignoreStones are xy of stones, we don´t know, if they are really on the board. Like the last robot set stone.
		# find out the camera setting where all stones on the board are detected correct
		return;

	def RemoveCapturesStonesFromBoard(self):
		removed = Board.RemovedStones(self._board, self._gnuGo.GetActualBoard());
		if (len(removed) > 0):
			self.Speak(_("Ich nehme nun {count} Steine vom Brett").format(count=len(removed)), wait=False);
			for stone in removed:
				self.RemoveCapturedStoneFromBoard(stone[0],stone[1]);

	def PlayAiStone(self,white=True):
		field = self._gnuGo.AiPlayWhite();
		self.UpdateFace();
		if (field==None):
			print("Error: gnuGo AI suggested no white stone?!?");
			return False;
		if (field=="PASS"):
			self.Speak(_("Ich passe!"), wait=False);
			return True;
		xyPos = self._board.AzToXy(field);
		print ("white AI stone to:", xyPos);
		successfulDropped = False;

		self.FindBestCameraSettings();

		while(successfulDropped == False):

			bot._motors.GrabStoneFromStorage();
			bot.PutStoneToFieldPos(xyPos[0],xyPos[1]);
			
			newStoneDetectionSuccessfull = False;
			while(newStoneDetectionSuccessfull == False):
				
				# check if stone really reached board
				newWhiteStones = self.GetNewStones(color=Board.White);
				if (len(newWhiteStones)==1):
					if (newWhiteStones[0] == xyPos):
						successfulDropped = True;
						newStoneDetectionSuccessfull = True;
					else:
						self.Speak(_("Oh, ich habe einen anderen neuen Stein, als den von mir gesetzten, erkannt."));
						self.Speak(_("Ich versuche, meine Kamera neu einzustellen."));
						self.Speak(_("Einen Augenblick bitte"), wait=False);
						self.FindBestCameraSettings(ignoreStones=[xyPos]);
						newStoneDetectionSuccessfull = False;
				else:
					if (len(newWhiteStones)==0):
						# set stone ist missing
						self.Speak(_("Oh, ich konnte wohl keinen Stein greifen. Bitte prüfe, dass mein Vorrat  nicht leer ist"));
						self.Speak(_("Ich versuche es noch einmal"), wait=False);
						# recalibreate y-axis
						self._motors.MoveToY(500);
						self._motors._yAxis.calibrateHome();
						newStoneDetectionSuccessfull = True;
					else:
						# more than 1 new stone detectec. re-set camera
						self.Speak(_("Oh, ich erkenne {count} neue weiße Steine.").format(count=len(newWhiteStones)));
						self.Speak(_("Ich versuche, meine Kamera neu einzustellen."));
						self.Speak(_("Einen Augenblick bitte"), wait=False);
						self.FindBestCameraSettings(ignoreStones=[xyPos]);
						newStoneDetectionSuccessfull = False;

		self._board.SetField(xyPos[0],xyPos[1],Board.White);
		return True;

	def PlayWhiteGame(self):
		self.ClearBoard();
		
		self.Speak(_("Bitte lege Deine schwarzen Vorgabe Steine auf das Brett. Drücke dann die Taste."), wait=False);
		self.WaitTillButtonPressed(color="green");
		
		# detect handycap stones
		self._motors.UpdateMotors();
		self._motors.UpdateGripperAndDispenser();
		handicapStones = self.GetNewStones(color=Board.Black);

		if (len(handicapStones) == 0):
			self.Speak(_("Du hast keine Vorgabe Steine gelegt."), wait=False);
			whiteToPlay = False;
		else:
			self.Speak(_("Du hast {count} Vorgabe Steine gelegt.").format(count=len(handicapStones)), wait=False);
			for stone in handicapStones:
				self._board.SetField(stone[0],stone[1],Board.Black);
				fieldAz = self._board.XyToAz(stone[0],stone[1]);
				print ("check set black: {field}".format(field=self._board.GetField(stone[0],stone[1])));
				self._gnuGo.PlayerPlayBlack(fieldAz);
			whiteToPlay = True;

		roundNo = 0;

		while(True):

			if (whiteToPlay):
				if (roundNo < 3):
					self.Speak(_("Ich bin am Zug. Bitte einen Augenblick Geduld."), wait=False);
					self.UpdateFace();
				if (self.PlayAiStone(white=True))==True:
					self.UpdateFace();
					whiteToPlay = False;
					roundNo = roundNo+1;
			else:
				self._motors.MoveOutOfCameraSight();
				self.Speak(_("Du bist am Zug."), wait=False);
				if (roundNo < 3):
					self.Speak(_("Bitte lege einen schwarzen Stein und drücke dann die Taste."), wait=False);
				self.FindBestCameraSettings();
				self.WaitTillButtonPressed(color="green");
				newBlackStones = self.GetNewStones(color=Board.Black);
				if (len(newBlackStones) == 0):
					self.Speak(_("Ich sehe keinen neuen schwarzen Stein"), wait=False);
				else:
					if (len(newBlackStones) == 1):
						for stone in newBlackStones:
							self._board.SetField(stone[0],stone[1],Board.Black);
							fieldAz = self._board.XyToAz(stone[0],stone[1]);
							self._gnuGo.PlayerPlayBlack(fieldAz);
							
							rnd = random.randrange(30);
							if (rnd==1):
								self.Speak(_("Ein interessanter Zug."),wait=False);
							elif (rnd==2):
								self.Speak(_("Wow, darauf wäre ich nicht gekommen."),wait=False);
							elif (rnd==3):
								self.Speak(_("Ok, das ist also Dein Zug."),wait=False);
							whiteToPlay = True;
							roundNo = roundNo+1;
					else:
						self.Speak(_("Ich sehe {count} statt einem neuen schwarzen Stein").format(count=len(newBlackStones)), wait=False);
						
			self.RemoveCapturesStonesFromBoard();

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down iGoBot")
			
			if (self._cameraStoneDetection != None):
				self._cameraStoneDetection.Release();
				
			if (self._camera != None):
				self._camera.Release();

			if (self._light != None):
				self._light.Off();
				self._light.Release();
				
			if (self._leds != None):
				self._leds.Release();
				
			if (self._speech != None):
				self._speech.Release();
				
			if (self._motors != None):
				self._motors.Release()

			if (self._gnuGo != None):
				self._gnuGo.Release();

			self._ended = True

	def __del__(self):
		self.Release()
		

		
def exit_handler():
	bot.Release()

if __name__ == "__main__":
	
	bot = iGoBot(boardSize=9)
	
	if (False):
		bot.Speak(_("Hallo"))
		bot.Speak(_("Möchtest Du eine Partie go mit mir spielen?"));
		bot.Speak(_("Ich habe eine Spielstärke von etwa 5 kyu."))
	
	atexit.register(exit_handler)
	
	#bot.StoreAllWhiteStones();
	
	#bot.MoveToXY(500,500);
	#time.sleep(10000);
	
	bot.PlayWhiteGame();
	
	#bot.StoreAllWhiteStones();
	
	
		#for i in range(1,1000):
		#	bot._leds.NeutralAndBlink();
		#	time.sleep(0.1);

	if (False):	
		for i in range(0,9):
			bot._motors.GrabStoneFromStorage();
			bot._motors.PutStoneToFieldPos(i,i);
	
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
					


        
        
        
        

    





