#!/usr/bin/env python

#     ###############################
#     # x-axis motor control module #
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

import time, sys, os

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/../libs" )

from GroveI2CMotorDriver import GroveI2CMotorDriver
from I2cIoExpanderPcf8574Synchron import I2cIoExpanderPcf8574Synchron
from StepperMotorControlSynchron import StepperMotorControlSynchron

class yAxis(StepperMotorControlSynchron):

	_motorName					= "yAxis"

	_i2CMotorDriverAddress		= 0x0f      # the address of the I2CMotorDriver

	_i2cIoExpanderPcf8574		= None      # the I2cIoExpanderPcf8574 the endstop is connected to
	_endStopBit					= 128       # the bit of the I2cIoExpanderPcf8574 to read the motor endstop

	#_stepData					= [0b0001,0b0101,0b0100,0b0110,0b0010,0b1010,0b1000,0b1001]  # the stepper motor step bits with half steps
	_stepData					= [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001]  # the stepper motor step bits with half steps
	#_stepData					= [0b0001,  0b0100,  0b0010, 0b1000]  # the stepper motor step bits
	#_stepData					= [0b1000, 0b0010 ,  0b0100, 0b0001]  # the stepper motor step bits
	MaxSteps					= 3800; #3900      # how many motor steps can the motor maximum move 
	
	#_stepData					= [0b0001, 0b0100, 0b0010, 0b1000, ]  # the stepper motor step bits with full steps
	#MaxSteps					= 800      # how many motor steps can the motor maximum move 

	_motor						= None
	_motorPowerOn				= 100
	_motorPowerStandBy			= 0
	_motorPowerOff				= 0
	_motorIsStandBy				= True
	
	_released					= False

	def __init__(self, address=0x0f, i2cIoExpanderPcf8574=None):
		super().__init__()
		self._i2CMotorDriverAdd=address
		self._i2cIoExpanderPcf8574 = i2cIoExpanderPcf8574
		self._motor = GroveI2CMotorDriver(self._i2CMotorDriverAdd)
		super().start()

		
	def _endStop(self):
		if (self._i2cIoExpanderPcf8574 == None):
			return False;
		return self._i2cIoExpanderPcf8574.getBit(self._endStopBit)

	def _updateMotorSteps(self):
		if (super()._releasedMotor == True):
			return
		#for i in range(1, 4):
		#actualStepDataPos = self.actualStepDataPos
		actualStepDataPos = self.actualStepDataPos
		if (self.lastStepDataPos != actualStepDataPos): # stepper has to move
			if (self._motorIsStandBy == True):
				self._motorIsStandBy = False
				self._motor.MotorSpeedSetAB(self._motorPowerOn,self._motorPowerOn)
			self._motor.MotorDirectionSet(self._stepData[actualStepDataPos])
			self.lastStepDataPos = actualStepDataPos
			self.lastStepDataPosChange = time.time()
		else:
			if (time.time() > self.lastStepDataPosChange + 5): # stepper has not moved in the last moments
				if (self._motorIsStandBy == False):
					self._motorIsStandBy = True
					self._motor.MotorSpeedSetAB(self._motorPowerStandBy,self._motorPowerStandBy) # last stepper move is long time ago
					print("off")
				
	def Release(self):
		if (self._released == False):
			super().ReleaseStepperMotor()
			self._released = True
			self._motor.MotorSpeedSetAB(self._motorPowerOff,self._motorPowerOff)

	def __del__(self):
		self.Release()

if __name__ == "__main__":
	time.sleep(2);
	
	endStop = I2cIoExpanderPcf8574Synchron(0x3e, useAsInputs=True)
	#endStop = None;
	motor = yAxis(0x0e, endStop)
	
	#time.sleep(1);
	
	sleeper = 0.0002;
	
	
	
	#motor._motor.MotorSpeedSetAB(motor._motorPowerOn,motor._motorPowerOn)
	
	
	
		
	#print ("backwards")
	if (False):
		test = 500;
		for i in range(1,test):
			motor._stepBackwards();
			motor._updateMotorSteps();
			time.sleep(sleeper);
			
		for i in range(1,test):
			motor._stepForward();
			motor._updateMotorSteps();
			time.sleep(sleeper);
	
	
	
	if (True):
		test = 2;
		for i in range(1,test):
			motor.targetPos = motor.MaxSteps 
			while motor.targetReached == False:
				motor.Update();
				time.sleep(motor._actualSpeedDelay);
				
			motor.targetPos =motor.MaxSteps * 0
			while motor.targetReached == False:
				motor.Update();
				time.sleep(motor._actualSpeedDelay);
			
	#time.sleep(1)
	#motor.Update();

	#for i in range(1, 4):
	#	motor.targetPos =motor.MaxSteps * 0.3
	#	while motor.targetReached == False:
			#print("wait for target "+ str(motor._targetPos))
			#motor.Update()
			#time.sleep(0.1)
	#		a=0

		#motor.SetTargetPos(0)
		#while motor.TargetReached() == False:
		#	print("wait for target "+ str(motor._targetPos))
		#	time.sleep(1)
		
	#	motor.targetPos = motor.MaxSteps * 0.5
	#	while motor.targetReached == False:
			#print("wait for target "+ str(motor._targetPos))
			#motor.Update()
	#		a=0
			#time.sleep(0.1)

	motor.Release()


