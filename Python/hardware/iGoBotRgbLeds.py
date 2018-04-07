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

	def AnimateButtonGreen(self):
		#self.rainbowCycle();
		#self.colorWipe(Color(127,0,0));
		self._leds.theaterChase(Color(127,0,0), countLed=self._buttonLedCount, startLed=self._buttonLedStart);
		#time.sleep(0.01);
	
	def ClearButton(self):
		for i in range(0, self._buttonLedCount):
			self._leds._pixels.setPixelColor(self._buttonLedStart+i, 0)
		self._leds._pixels.show()     

	def Speak(self):
		self._face.Speak();
		
	def NeutralFace(self, red=255, green=255, blue=255):
		self._face.showFace(self._face.neutral, red, green, blue);
		
	def NeutralAndBlink(self, red=255, green=255, blue=255):
		self._face.NeutralAndBlink(red, green, blue);

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
	for i in range(1,10):
		leds.AnimateButtonGreen();
	for i in range(1,10):
		leds.Speak();
		time.sleep(0.1);
	leds.Release()









