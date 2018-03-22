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
from I2cIoExpanderPcf8574 import I2cIoExpanderPcf8574
from StepperMotorControlSynchron import StepperMotorControlSynchron

class NeckLeftRight(StepperMotorControlSynchron):

	_motorName					= "x axis"

	_i2CMotorDriverAddress		= 0x0d      # the address of the I2CMotorDriver

	_i2cIoExpanderPcf8574		= None      # the I2cIoExpanderPcf8574 the endstop is connected to
	_endStopBit					= 32       # the bit of the I2cIoExpanderPcf8574 to read the motor endstop

	_isClosedCircle				= False      # is 0 to maxSteps a full round to the same endstop

	_fastestSpeedDelay			= 0.0001     # how fast can the stepper motor go
	_slowestSpeedDelay			= _fastestSpeedDelay * 10
	_calibrateSpeedDelay		= _fastestSpeedDelay * 5
	_actualSpeedDelay			= _slowestSpeedDelay

	_rampSpeedup				= 1.01       # how fast is the speed of for motor ramping
	_rampSafeArea				= 20         # prevent to come nearer than this to the endstop

	_stepData					= [0b0001,0b0101,0b0100,0b0110,0b0010,0b1010,0b1000,0b1001]  # the stepper motor step bits with half steps
	#_stepData					= [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001]  # the stepper motor step bits with half steps
	#_stepData					= [0b0001,  0b0100,  0b0010, 0b1000]  # the stepper motor step bits
	#_stepData					= [0b1000, 0b0010 ,  0b0100, 0b0001]  # the stepper motor step bits
	MaxSteps					= 4100      # how many motor steps can the motor maximum move 
	
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
			if (time.time() > self.lastStepDataPosChange + 1): # stepper has not moved in the last moments
				if (self._motorIsStandBy == False):
					self._motorIsStandBy = True
					self._motor.MotorSpeedSetAB(self._motorPowerStandBy,self._motorPowerStandBy) # last stepper move is long time ago
					#print("off")
				
	def Release(self):
		if (self._released == False):
			super().ReleaseStepperMotor()
			self._released = True
			self._motor.MotorSpeedSetAB(self._motorPowerOff,self._motorPowerOff)

	def __del__(self):
		self.Release()

if __name__ == "__main__":
	endStop = I2cIoExpanderPcf8574(0x3e, useAsInputs=True)
	#endStop = None;
	motor = NeckLeftRight(0x0d, endStop)
	
	#time.sleep(1);
	
	for i in range(1,20):
		motor.targetPos = motor.MaxSteps #* 0.1
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


