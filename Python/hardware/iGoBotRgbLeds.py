#!/usr/bin/env python

#     ##########################
#     # RGB LED control module #
#     ##########################
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

from __future__ import division
import time, sys, os

my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])

sys.path.insert(0,my_path + "/../DanielsRasPiPythonLibs/hardware/" )

import time
from neopixel import *
from RgbLeds import RgbLeds
from McRoboFace import McRoboFace

class iGoBotRgbLeds():

	_leds				= None;
	_face				= None;

	_buttonLedStart		= 17;
	_buttonLedCount		= 12;

	_released			= False
	
	def __init__(self):
		self._leds = RgbLeds(ledCount=29, ledBrightness=100);
		self._face = McRoboFace(self._leds);

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
		self._leds.theaterChase(Color(127,0,0));
		#time.sleep(0.01);


	def Release(self):
		if (self._released == False):
			self._released = True
			print("iGoBotRgbLeds releasing")
			self._leds.Release();
			self._face.Release();

	def __del__(self):
		self.Release()    

if __name__ == "__main__":

	leds = iGoBotRgbLeds();
	time.sleep(2);
	leds.Release()









