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
#     ##############
#     # motors lib #
#     ##############
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

from __future__ import division

import os, sys
from os.path import abspath

import time, sys, os

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/../" )

import time

import math
import grovepi

from DanielsRasPiPythonLibs.hardware.PCF8574 import PCF8574
from DanielsRasPiPythonLibs.hardware.I2cIoExpanderPcf8574Synchron import I2cIoExpanderPcf8574Synchron
from DanielsRasPiPythonLibs.hardware.StepperMotorControlSynchron import StepperMotorControlSynchron
from hardware.GripperAndDispenser import GripperAndDispenser

import atexit

class Motors:

	_xAxisAdress					= 0x0d
	_yAxisAdress					= 0x0e
	_zAxisAdress					= 0x0f
	_gripperAdress					= 0x40

	_released						= False

	_xAxis 							= None;
	_yAxis 							= None;
	_zAxis 							= None;
	_gripperAndDispenser			= None;
	_switches 						= None;
	
	_xPosDropCapturedBlack			= 200;
	_xPosDropCapturedWhite			= 4000;
	
	# where to move to drop the stone into the drop storage
	_xPosStoneStorageDrop			= 4400
	_yPosStoneStorageDrop			= 3800
	
	# where to move to grab a new stone from dispenser
	_xPosStoneStorageGrab			= 4170 
	_yPosStoneStorageGrab			= 3485
	
	_yPosOutOfCameraSight			= 3800
	
	_zPosMaxUp						= 0;
	_zPosUp							= 400;
	_zPosDropOnBoard				= 600;
	_zPosOnBoard					= 635;
	_zPosOnDispenserGrab			= 700;
	
	def __init__(self, switches):
		self._switches = switches;
		
		self._gripperAndDispenser = GripperAndDispenser(i2cAdress=self._gripperAdress, busnum=1)
		self._gripperAndDispenser.openGripper();
		
		endStop = switches;
		self._zAxis = StepperMotorControlSynchron("z-axis", self._zAxisAdress, 940,   endStop,  64, [0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001, 0b1001], autoStandBy=False, targetOnlyEvenSteps=True, rampSafeArea=20)
		self._xAxis = StepperMotorControlSynchron("x-axis", self._xAxisAdress, 4400,  endStop,  32, [0b0001, 0b0101, 0b0100, 0b0110, 0b0010, 0b1010, 0b1000, 0b1001], autoStandBy=False, targetOnlyEvenSteps=True,)
		self._yAxis = StepperMotorControlSynchron("y-axis", self._yAxisAdress, 3800,  endStop, 128, [0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001, 0b1001], autoStandBy=False, targetOnlyEvenSteps=True,)
		
		self.WaitForAllMotors();
		
		self.MoveToZ(self._zPosUp);
		return;
		
	## axis motors ------------------------------
	
	def StandByAllMotors(self):
		self._xAxis.StandBy();
		self._yAxis.StandBy();
		self._zAxis.StandBy();

	def WakeUpAllMotors(self):
		self._xAxis.EndStandBy();
		self._yAxis.EndStandBy();
		self._zAxis.EndStandBy();
				
	
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
		if (self._yAxis.targetPos == pos):
			 return;
		overdrive = 100;
		if (self._yAxis.targetPos > pos):
			self._yAxis.targetPos = pos - overdrive;
		else:
			self._yAxis.targetPos = pos + overdrive;
		self.WaitForAllMotors();
		self._yAxis.targetPos = pos;
		self.WaitForAllMotors();
		
	def MoveToZ(self, pos):
		self._zAxis.targetPos = pos;
		self.WaitForAllMotors();
		
	def MoveOutOfCameraSight(self):
		self.MoveToZ(self._zPosMaxUp);
		self.MoveToY(self._yPosOutOfCameraSight);
		
	## gripper and dispenser -----------------------
	
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
			
	def UpdateGripperAndDispenser(self):
		self._gripperAndDispenser.Update();
			
	## stone interaction -----------------------
	
	def DropCapturedStone(self, black):
		if (black):
			self.MoveToX(self._xPosDropCapturedBlack);
		else:
			self.MoveToX(self._xPosDropCapturedWhite);
		self.PutStoneToBoard();

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

	def TakeStoneFromPosition(self,stepperX,stepperY):
		self._MoveToXY(stepperX,stepperY);
		self.TakeStoneFromBoard();

	def PutStoneToPosition(self, stepperX, stepperY):
		self.MoveToXY(stepperX, stepperY);
		self.PutStoneToBoard();
		
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
		
	## -----------------------------------------------------

	def Release(self):
		if (self._released == False):
			self._released = True
			print ("shutting down motors")

			if (self._zAxis != None):
				self.MoveToZ(0);
				self._zAxis.Release()
			
			if (self._xAxis != None):
				self.MoveToX(0);
				self._xAxis.Release()

			if (self._yAxis != None):
				self.MoveToY(0);
				self._yAxis.Release()
			
			if (self._gripperAndDispenser != None):
				self._gripperAndDispenser.openGripper();
				while(self._gripperAndDispenser.allTargetsReached == False):
					self._gripperAndDispenser.Update();
				self._gripperAndDispenser.Release();

	def __del__(self):
		self.Release()
		
def exit_handler():
	motors.Release()

if __name__ == "__main__":
	
	switches = I2cIoExpanderPcf8574Synchron(0x3e, useAsInputs=True)
	
	motors= Motors(switches=switches)
	motors.GrabStoneFromStorage();
	
	atexit.register(exit_handler)



