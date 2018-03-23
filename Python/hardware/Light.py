#!/usr/bin/env python

#     #################
#     # light control #
#     #################
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
import grovepi


class Light():
	
	_groveRelaisPort = 8;
	
	def __init__(self, groveRelaisDigitalPort):
		self._grovePort = groveRelaisDigitalPort
		grovepi.pinMode(self._groveRelaisPort, "OUTPUT")

	def On(self):
		grovepi.digitalWrite(self._groveRelaisPort,1)
		
	def Off(self):
		grovepi.digitalWrite(self._groveRelaisPort,0)
	
	def Release(self):
		self.Off();

	def __del__(self):
		self.Release()
		
		
import atexit
		
def exit_handler():
	right.Release()

if __name__ == "__main__":
	
	light = Light(8);
	
	for i in range(1,3):
		light.On();
		time.sleep(1);
		light.Off();
		time.sleep(1);
	
