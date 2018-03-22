#!/usr/bin/env python

#     ########################
#     # gripper servo module #
#     ########################
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
import time, sys, os

import atexit

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/../libs" )

#from I2cIoExpanderPcf8574Synchron import I2cIoExpanderPcf8574Synchron

from array import array
import Adafruit_PCA9685

from SharedInts import SharedInts
from SharedFloats import SharedFloats

class Gripper():
	
	_pwm		= None
	_released 	= False
	
	_servoCount = 1;

	_gripperOpen	= 340
	_gripperClosed	= 200
	
	_lastUpdateTime	= time.time()
	
	__last_servo_set_time = 0;
	
	allTargetsReached = False;
	
	_actualSpeedDelay = 0.01
	_maxStepsPerSecond = 190
	
	_name 		= "gripper"
	
	_targets 					= [0]
	_values						= [0.0]

	
	def __init__(self, i2cAdress, busnum):

		self.__last_servo_set_time = 0

		# Initialise the PCA9685 using the default address (0x40).
		#self._pwm = Adafruit_PCA9685.PCA9685()
		# Alternatively specify a different address and/or bus:
		self._pwm = Adafruit_PCA9685.PCA9685(address=i2cAdress, busnum=busnum)
		
		# Set frequency to 60hz, good for servos.
		self._pwm.set_pwm_freq(60)
		
		# reset servo
		self._targets[0] = int(self._gripperOpen);
		self._values[0] = int(self._gripperOpen);
		self.setServo(0, int(self._gripperOpen))	
	
		
	def Update(self):
		timeDiff = time.time() - self._lastUpdateTime
		if (timeDiff < self._actualSpeedDelay):
			time.sleep(self._actualSpeedDelay - timeDiff)
		time.sleep(self._actualSpeedDelay)
		timeDiff = time.time() - self._lastUpdateTime
		timeDiff = min(timeDiff, self._actualSpeedDelay * 2)
		allReached = True
		maxSpeed = self._maxStepsPerSecond * timeDiff
		#print(maxSpeed)
		for i in range(0,self._servoCount):
			reachedThis = True
			diff = int(self._targets[i] - self._values[i])
			plus = 0
			if (diff > 0):
				plus = max(0.1, min(diff , maxSpeed))
				reachedThis = False
			if (diff < 0):
				plus = min(-0.1, max(diff , -maxSpeed))
				reachedThis = False
			if (reachedThis == False):
				allReached = False
				newValue = self._values[0] + plus
				self._values[i] = newValue;
				self.setServo(i,newValue)
		self.allTargetsReached = allReached
		self._lastUpdateTime = time.time()
		
		if (self.__last_servo_set_time + 5 < time.time()):
			# long time nothing done
			#self.power_off()
			time.sleep(0.5)
		
		#print("update end")

	def openGripper(self):
		self._targets[0] = self._gripperOpen;
		self.allTargetsReached = False
		self.waitTillTargetReached();

	def closeGripper(self):
		self._targets[0] = self._gripperClosed;
		self.allTargetsReached = False
		self.waitTillTargetReached();

	def waitTillTargetReached(self):
		while (self.allTargetsReached == False):
			self.Update();
			time.sleep(self._actualSpeedDelay)
			
	def setServo(self, port, value):
		self._pwm.set_pwm(port, 0, int(value))
		self.__last_servo_set_time = time.time()
		#self.power_on()
		
	def portDemo(self, port):
		self.setServo(port,0)
		self.allTargetsReached = False
		time.sleep(1)
		self.setServo(port,100)
		self.allTargetsReached = False
		time.sleep(1)
		self.setServo(port, int(self._handArmHomeValues[port]))
		self.allTargetsReached = False
		time.sleep(1)
		
	def turnOff(self):
		print("turning off " + self._name)
		for i in range(0,self._servoCount):
			self._pwm.set_pwm(i, 0, 0)
		#self.power_off()

	def Release(self):
		if (self._released == False):
			print("releasing " + self._name)
			#self.home()
			self.openGripper();
			self._released = True
			self.turnOff()
			print("super().EndUpdating() " + self._name)
			
	def __del__(self):
		self.Release()
		
def exit_handler():
	right.Release()

if __name__ == "__main__":
	
	#relais = RelaisI2C(I2cIoExpanderPcf8574(address=0x39, useAsInputs=False))
	
	right = Gripper(i2cAdress=0x40, busnum=1)
	
	atexit.register(exit_handler)
	
	time.sleep(2)
	
	right.closeGripper();
	time.sleep(1)
	right.openGripper();
	time.sleep(1)
