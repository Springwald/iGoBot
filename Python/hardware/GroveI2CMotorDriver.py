#!/usr/bin/env python
#
# GrovePi Library for using the Grove - I2C Motor Driver(http://www.seeedstudio.com/depot/Grove-I2C-Motor-Driver-p-907.html)
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi
#
# Have a question about this library?  Ask on the forums here:  http://www.dexterindustries.com/forum/?forum=grovepi
#
'''
## License

The MIT License (MIT)

GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
Copyright (C) 2015  Dexter Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import time,sys
import RPi.GPIO as GPIO
import smbus

# use the bus that matches your raspi version
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
	bus = smbus.SMBus(1)
else:
	bus = smbus.SMBus(0)

class GroveI2CMotorDriver:
	
	MotorSpeedSet             = 0x82
	PWMFrequenceSet           = 0x84
	DirectionSet              = 0xaa
	MotorSetA                 = 0xa1
	MotorSetB                 = 0xa5
	Nothing                   = 0x01
	EnableStepper             = 0x1a
	UnenableStepper           = 0x1b
	Stepernu                  = 0x1c
	I2CMotorDriverAdd         = 0x0f  #Set the address of the I2CMotorDriver

	def __init__(self,address=0x0f):
		self.I2CMotorDriverAdd=address

	#Maps speed from 0-100 to 0-255
	def map_vals(self,value, leftMin, leftMax, rightMin, rightMax):
		#http://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
		# Figure out how 'wide' each range is
		leftSpan = leftMax - leftMin
		rightSpan = rightMax - rightMin

		# Convert the left range into a 0-1 range (float)
		valueScaled = float(value - leftMin) / float(leftSpan)

		# Convert the 0-1 range into a value in the right range.
		return int(rightMin + (valueScaled * rightSpan))
		
	#Set motor speed
	def MotorSpeedSetAB(self,MotorSpeedA,MotorSpeedB):
		MotorSpeedA=self.map_vals(MotorSpeedA,0,100,0,255)
		MotorSpeedB=self.map_vals(MotorSpeedB,0,100,0,255)
		bus.write_i2c_block_data(self.I2CMotorDriverAdd, self.MotorSpeedSet, [MotorSpeedA,MotorSpeedB])
		time.sleep(.002)
	
	#Set motor direction
	def MotorDirectionSet(self,Direction):
		bus.write_i2c_block_data(self.I2CMotorDriverAdd, self.DirectionSet, [Direction,0])
		#time.sleep(.002)
		
if __name__ == "__main__":
	tester = GroveI2CMotorDriver(0x0e);
	
	tester.MotorSpeedSetAB(100,100);
	#_stepData = [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001]  # the stepper motor step bits with half steps
	#_stepData = [0b0001, 0b1000, 0b0010, 0b0100]  # the stepper motor step bits with half steps
	_stepData = [0b1001, 0b1000, 0b1010, 0b0010, 0b0110, 0b0100, 0b0101, 0b0001];
	
	speed = 0.0002;
	length = 60;
	
	for n in range(0,3):
		for n in range(0,length):
			for i in range(0, len(_stepData)):
				tester.MotorDirectionSet(_stepData[i]);
				time.sleep(speed);
		for n in range(0,length):
			for i in range(len(_stepData)-1,-1,-1):
				#print(i)
				tester.MotorDirectionSet(_stepData[i]);
				time.sleep(speed);
				
	tester.MotorSpeedSetAB(0,0);
