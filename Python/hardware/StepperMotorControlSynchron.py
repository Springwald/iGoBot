#!/usr/bin/env python

#     #########################################
#     # abstract stepper motor control module #
#     #########################################
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
from I2cIoExpanderPcf8574 import I2cIoExpanderPcf8574

class StepperMotorControlSynchron():

	_motorName						= "untitled"

	targetPos				= 0
	calibrating				= False
	actualPos				= 0 # 0=endstop pos, StepsProRound=360°
	actualStepDataPos		= 0
	lastStepDataPos			= 0
	lastStepDataPosChange	= 0

	MaxSteps						= 1600      # how many motor steps can the motor maximum move 

	_isClosedCircle					= True      # is 0 to maxSteps a full round to the same endstop

	_fastestSpeedDelay				= 0.002     # how fast can the stepper motor go
	_slowestSpeedDelay				= _fastestSpeedDelay * 2 
	_calibrateSpeedDelay			= _fastestSpeedDelay * 5 
	_actualSpeedDelay				= _slowestSpeedDelay

	_rampSpeedup					= 1.05      # how fast is the speed of for motor ramping
	_rampDistance					= 0         # how many steps before the target pos start to ramp down (calculated automatically)
	_rampSafeArea					= 35        # prevent to come nearer than this to the endstop

	_stepData						= []  # the stepper motor step bits

	_releasedMotor					= False

	def __init__(self):
		print ("init " + self._motorName + " speed:" + str(self._fastestSpeedDelay ) + " slowest:" + str(self._slowestSpeedDelay))

		self.actualPos = 0
		self.targetPos = 0
		self.actualStepDataPos = 0
		self.lastStepDataPos = -1
		self.lastStepDataPosChange = 0

	@property
	def targetReached(self):
		return int(self.actualPos) == int(self.targetPos)
	
	def start(self):
		self.calibrating = False
		#self.calibrateHome()
		self._calculateRampDistance();

	def _endStop(self): # True: endstop is reached
		raise Exception("not implemented!")

	def _updateMotorSteps(self): # write motor data to steps
		raise Exception("not implemented!")
		

	def Update(self):

		if (self.calibrating == True): 
			time.sleep(1)
			#print ("NOT! updating " + self._motorName)
			return

		#print ("updating " + self._motorName + " :" + str(self.GetActualPos()))
		# Check if unexpected end top contact
		if (self._endStop()):
			print ("oha - the endstop of motor " + self._motorName + " is reached this should not happen when running normal")
			# oha - the endstop is reached this should not happen when running normal
			if (self.actualPos > self.MaxSteps / 2):
				# is over the half round -> drive back half a round
				for i in range(1, int(self.MaxSteps / 2)):
					self._stepBackwards()
					self._updateMotorSteps()
			#else:
				# is under the half round -> calibrate normal
			self.calibrateHome()

		# check if have to move to target
		#timeSinceLastUpdate = time.time() - self.lastStepDataPosChange
		#if (timeSinceLastUpdate < self._actualSpeedDelay):
		#	time.sleep((self._actualSpeedDelay - timeSinceLastUpdate)/2)
        
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
				
			#self._actualSpeedDelay  = self._fastestSpeedDelay;
				
			if (int(distance) > 0):
				self._stepForward()
				self._updateMotorSteps()
			else:
				if (int(distance) < 0):
					self._stepBackwards()
					self._updateMotorSteps()
				else:
					self._updateMotorSteps()
					time.sleep(0.5)
					
		self._actualSpeed = self._fastestSpeedDelay;

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
		print ("calibrating motor " + self._motorName  + ": free endstop, isClosedCircle=" + str(self._isClosedCircle));
		while self._endStop() == True: # backwards if on endstop
			#if (self.actualPos < self.MaxSteps /2) and (self._isClosedCircle == True):
			self._stepForward()
			#else:
			#	self._stepBackwards()
			self._updateMotorSteps()
			time.sleep(self._calibrateSpeedDelay)

		print ("calibrating motor " + self._motorName  + ": find endstop")
		while self._endStop() == False: # forward till on endstop
			self._stepBackwards();
			self._updateMotorSteps()
			time.sleep(self._calibrateSpeedDelay)

		self.actualPos =0

		print ("calibrating motor " + self._motorName  + ": move out of safe area")
		for i in range(1, int(self._rampSafeArea)): # move out of safe area
			self._stepForward()
			self._updateMotorSteps()
			time.sleep(self._calibrateSpeedDelay)

		self.targetPos = self.actualPos
		print ("motor " + self._motorName + " calibrated")
		self.calibrating = False
        
	def ReleaseStepperMotor(self):
		if (self._releasedMotor == False):
			print ("shutting down " + self._motorName)
			self.targetPos = 0
			while self.targetReached == False:
				print("wait till targetReached");
				self.Update();
				time.sleep(self._fastestSpeedDelay);
				#print ("shutting down " + self._motorName+ str(self.GetActualPos()) + ">" + str(self._targetPos))
			self._releasedMotor = True
    
if __name__ == "__main__":
	print("no tests for abstract class StepperMotorControl available")

