#!/usr/bin/env python

#     ##################################
#     # RGB LED control module #
#     ##################################
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


#!/usr/bin/python
# mcroboface.py

import time
from neopixel import *

class RgbLeds():

	# LED strip configuration:
	Start_LED_FACE		= 0		 # LEDs before the McRoboFace
	LED_COUNT_FACE		= 17
	Start_LED_BUTTON	= LED_COUNT_FACE	 # LEDs before the Button
	LED_COUNT_BUTTON	= 12
	LED_COUNT      		= LED_COUNT_FACE+LED_COUNT_BUTTON   # Number of LED pixels.
	LED_PIN        		= 18		# GPIO pin connected to the pixels (must support PWM!).
	LED_FREQ_HZ    		= 800000	# LED signal frequency in hertz (usually 800khz)
	LED_DMA        		= 5			# DMA channel to use for generating signal (try 5)
	LED_BRIGHTNESS 		= 64		# Set to 0 for darkest and 255 for brightest
	LED_INVERT     		= False		# True to invert the signal (when using NPN transistor level shift)
	
	_pixels				= None;
	_released			= False

	# Define various facial expressions
	smileData   = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
	frownData   = [1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1]
	grimaceData = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1]
	oooohData   = [0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1]
	
	def __init__(self):
		# Initialis the McRoboFace controllers
		self._pixels = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS)
		self._pixels.begin()

	def clearFace(self):
		for i in range(0, self.Start_LED_FACE + self.LED_COUNT_FACE):
			self._pixels.setPixelColor(i, 0)
			self._pixels.show()   
			
	def clearButton(self):
		for i in range(0, self.Start_LED_BUTTON + self.LED_COUNT_BUTTON):
			self._pixels.setPixelColor(i, 0)
			self._pixels.show()                                       

	def showFace (self, data, Red, Green, Blue):
		for i in range(0, len(data)):
			if (data[i] > 0):
				self._pixels.setPixelColor(self.Start_LED_FACE+i, Color(Green, Red, Blue))
			else:
				self._pixels.setPixelColor(self.Start_LED_FACE+i, 0)
		self._pixels.show()           

	def theaterChase(self, color, wait_ms=50, iterations=1):
	#Movie theater light style chaser animation."""
		for j in range(iterations):
			for q in range(3):
				for i in range(0, self.LED_COUNT_BUTTON, 3):
					self._pixels.setPixelColor(self.Start_LED_BUTTON+i+q, color)
				self._pixels.show()
				time.sleep(wait_ms/1000.0)
				for i in range(0, self.LED_COUNT_BUTTON, 3):
					self._pixels.setPixelColor(self.Start_LED_BUTTON+i+q, 0)
					
	def colorWipe(self, color, wait_ms=0.1):
		#Wipe color across display a pixel at a time.
		for i in range(self.LED_COUNT_BUTTON):
			self._pixels.setPixelColor(self.Start_LED_BUTTON+i , color)
			self._pixels.show()
			time.sleep(wait_ms/1000.0)
			

	def wheel(self,pos):
		#Generate rainbow colors across 0-255 positions."""
		if pos < 85:
			return Color(pos * 3, 255 - pos * 3, 0)
		elif pos < 170:
			pos -= 85
			return Color(255 - pos * 3, 0, pos * 3)
		else:
			pos -= 170
			return Color(0, pos * 3, 255 - pos * 3)
			
	def rainbowCycle(self, wait_ms=10, iterations=1):
		"""Draw rainbow that uniformly distributes itself across all pixels."""
		strip = self._pixels
		for j in range(256*iterations):
			for i in range(self.LED_COUNT_BUTTON):
				strip.setPixelColor(self.Start_LED_BUTTON+i, self.wheel(((int(i * 256 / strip.numPixels()) + j) & 255)))
			strip.show()
			time.sleep(wait_ms/1000.0)

	def AnimateButtonGreen(self):
		#self.rainbowCycle();
		#self.colorWipe(Color(127,0,0));
		self.theaterChase(Color(127,0,0));
		#time.sleep(0.01);

	def McRoboFaceDemo(self):
		try:
			self.clearFace()
			self.showFace (self.smileData, 255, 0 , 0)
			time.sleep(2)
			self.showFace (self.frownData, 0, 0, 255)
			time.sleep(2)
			self.showFace (self.grimaceData, 255, 0, 255)
			time.sleep(2)
			self.showFace (self.oooohData, 0, 255, 0)
			time.sleep(2)
		except KeyboardInterrupt:
			print
		finally:
			self.clearFace()

	def Release(self):
		if (self._released == False):
			self._released = True
			print("RGB LEDs releasing")
			self.clearFace();
			self.clearButton();

	def __del__(self):
		self.Release()    

if __name__ == "__main__":

	leds = RgbLeds();

	for i in range(1,20):
		leds.AnimateButtonGreen();
	
	leds.McRoboFaceDemo();

	leds.Release()









