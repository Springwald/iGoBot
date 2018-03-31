#!/usr/bin/env python

#     ################################
#     # stepper motor control module #
#     ################################
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

import time
from GroveI2CMotorDriver import GroveI2CMotorDriver
from I2cIoExpanderPcf8574Synchron import I2cIoExpanderPcf8574Synchron

class StepperMotorControlSynchron():

	_motorName						= "untitled"

	___targetPos			= 0
	calibrating				= False
	actualPos				= 0 
	actualStepDataPos		= 0
	lastStepDataPos			= 0
	lastStepDataPosChange	= 0
	
	_i2cIoExpanderPcf8574		= None      # the I2cIoExpanderPcf8574 the endstop is connected to
	_endStopBit					= 0       # the bit of the I2cIoExpanderPcf8574 to read the motor endstop

	_fastestSpeedDelay			= 0.00005     # how fast can the stepper motor go
	_slowestSpeedDelay			= _fastestSpeedDelay * 20
	_calibrateSpeedDelay		= _fastestSpeedDelay * 20
	_actualSpeedDelay			= _slowestSpeedDelay
	
	_rampSpeedup				= 1.02      # how fast is the speed of for motor ramping
	_rampSafeArea				= 50         # prevent to come nearer than this to the endstop
	_rampDistance				= 0        # how many steps before the target pos start to ramp down (calculated automatically)


	_stepData						= []  #	 the stepper motor step bits
	
	_motor						= None
	_motorPowerOn				= 100
	_motorPowerStandBy			= 0
	_motorPowerOff				= 0
	_motorIsStandBy				= True

	_releasedMotor					= False
	_released					= False

	def __init__(self, name, address, maxSteps, i2cIoExpanderPcf8574, i2cIoExpanderPcf8574Bit, stepData, rampSafeArea = 50):
		self._maxSteps = maxSteps;
		self._motorName = name;
		self._i2cIoExpanderPcf8574 = i2cIoExpanderPcf8574;
		self._endStopBit = i2cIoExpanderPcf8574Bit;
		self._stepData = stepData;
		self._rampSafeArea = rampSafeArea;
		self.actualPos = 0
		self.targetPos = 0
		self.actualStepDataPos = 0
		self.lastStepDataPos = -1
		self.lastStepDataPosChange = 0
		self._motor = GroveI2CMotorDriver(address)
		self.start()
		
	@property
	def targetPos(self):
		return self.___targetPos
	@targetPos.setter
	def targetPos(self, targetPos):
		#print (self.__targetPosKey)
		targetPos = int(min(self._maxSteps - self._rampSafeArea, targetPos))
		targetPos = int(max(self._rampSafeArea, targetPos))
		self.___targetPos = targetPos

	@property
	def targetReached(self):
		return int(self.actualPos) == int(self.targetPos)
	
	def start(self):
		self.calibrating = False
		self.calibrateHome()
		self._calculateRampDistance();
		
	def _endStop(self):
		if (self._i2cIoExpanderPcf8574 == None):
			print("no endstop attached");
			return False;
		return self._i2cIoExpanderPcf8574.getBit(self._endStopBit)

	def _updateMotorSteps(self):
		if (self._releasedMotor == True):
			return
		
		actualStepDataPos = self.actualStepDataPos
		if (self.lastStepDataPos != actualStepDataPos): # stepper has to move
			if (self._motorIsStandBy == True):
				self._motorIsStandBy = False
				time.sleep(0.1)
				self._motor.MotorSpeedSetAB(self._motorPowerOn,self._motorPowerOn)
			self._motor.MotorDirectionSet(self._stepData[actualStepDataPos])
			self.lastStepDataPos = actualStepDataPos
			self.lastStepDataPosChange = time.time()
			time.sleep(self._actualSpeedDelay);
			#print(self._actualSpeedDelay);
		else:
			if (time.time() > self.lastStepDataPosChange + 3): # stepper has not moved in the last moments
				if (self._motorIsStandBy == False):
					self._motorIsStandBy = True
					self._motor.MotorSpeedSetAB(self._motorPowerStandBy,self._motorPowerStandBy) # last stepper move is long time ago
					#print("off")

	def Update(self):
		if (self.calibrating == True): 
			return
       
		# check if stepper update can be done
		if (self.targetReached==True):
			self._actualSpeedDelay = self._slowestSpeedDelay
			self._updateMotorSteps()
		else:
			distance = self.targetPos - self.actualPos
			if (abs(distance) < self._rampDistance): # getting slow when near to target
				# is near to target 
				if (self._actualSpeedDelay < self._slowestSpeedDelay):
					self._actualSpeedDelay = min(self._slowestSpeedDelay, self._actualSpeedDelay * self._rampSpeedup)
			else:
				# far away from target
				if (self._actualSpeedDelay > self._fastestSpeedDelay):
					self._actualSpeedDelay= max(self._fastestSpeedDelay, self._actualSpeedDelay / self._rampSpeedup)

			if (int(distance) > 0):
				self._stepForward()
				self._updateMotorSteps()
			else:
				if (int(distance) < 0):
					self._stepBackwards()
					self._updateMotorSteps()
				else:
					self._updateMotorSteps()

	def _calculateRampDistance(self):
		self._rampDistance = 0;
		testSpeed = self._slowestSpeedDelay
		while testSpeed > self._fastestSpeedDelay:
			self._rampDistance += 1
			testSpeed = testSpeed / self._rampSpeedup
        
	def _stepBackwards (self):
		#print ("_stepBackwards motor " + self._motorName )
		actualStepDataPos = self.actualStepDataPos
		actualStepDataPos += 1
		if actualStepDataPos > len(self._stepData)-1:
			actualStepDataPos = 0
		self.actualStepDataPos = actualStepDataPos
		self.actualPos = self.actualPos - 1
        
	def _stepForward(self):
		#print ("_stepBackwards motor " + self._motorName )
		actualStepDataPos = self.actualStepDataPos
		actualStepDataPos -= 1
		if actualStepDataPos < 0:
			actualStepDataPos = len(self._stepData)-1
		self.actualStepDataPos = actualStepDataPos
		self.actualPos =  self.actualPos + 1

	def calibrateHome(self):
		self.calibrating = True
		
		print ("calibrating motor " + self._motorName )
		print ("calibrating motor " + self._motorName  + ": free endstop");
		
		self._actualSpeedDelay = self._calibrateSpeedDelay;
		
		while self._endStop() == True: # backwards if on endstop
			self._stepForward()
			self._updateMotorSteps()

		print ("calibrating motor " + self._motorName  + ": find endstop")
		while self._endStop() == False: # forward till on endstop
			self._stepBackwards();
			self._updateMotorSteps()

		self.actualPos =0

		print ("calibrating motor " + self._motorName  + ": move out of safe area")
		for i in range(1, int(self._rampSafeArea)): # move out of safe area
			self._stepForward()
			self._updateMotorSteps()
			
		self.actualPos =0

		self.targetPos = self.actualPos
		print ("motor " + self._motorName + " calibrated")
		self.calibrating = False
        
	def ReleaseStepperMotor(self):
		if (self._releasedMotor == False):
			print ("shutting down motor " + self._motorName)
			self.targetPos = 0
			while self.targetReached == False:
				#print("wait till targetReached");
				self.Update();
				time.sleep(self._fastestSpeedDelay);
				#print ("shutting down " + self._motorName+ str(self.GetActualPos()) + ">" + str(self._targetPos))
			self._releasedMotor = True
			
	def Release(self):
		if (self._released == False):
			self.ReleaseStepperMotor()
			self._released = True
			self._motor.MotorSpeedSetAB(self._motorPowerOff,self._motorPowerOff)

	def __del__(self):
		self.Release()
    

if __name__ == "__main__":
	time.sleep(2);
	
	endStop = I2cIoExpanderPcf8574Synchron(0x3e, useAsInputs=True)
	motor = StepperMotorControlSynchron("y-axis", 0x0e, 3800,  endStop, 128, [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001])
			
	sleeper = 0.0002;


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
			motor.targetPos = motor._maxSteps 
			print(motor.targetPos);
			while motor.targetReached == False:
				motor.Update();
				time.sleep(motor._actualSpeedDelay);
				
			motor.targetPos =motor._maxSteps * 0
			print(motor.targetPos);
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
