#!/usr/bin/env python

#     ########################
#     # speech output module #
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



import time
import os, sys
import subprocess
import pygame
from pygame.locals import *

sys.path.insert(0, os.path.abspath("libs"))

class SpeechOutput():

	_released					= False;
	_soundcard					= None;
	_aplay_process				= None;

	def __init__(self, soundcard="sysdefault", voice="-vde"):  
		# soundCard: "plughw:1" for Soundcard 1; "sysdefault" for standard soundcard
		# voice: "-vde" for german robotic; "-vmb-de2", for german male
		self._soundcard = soundcard;
		self._voice = voice;
		print("speech init")
		
	def IsSpeaking(self):
		if (self._aplay_process != None):
			if (self._aplay_process.poll() == None):
				return True
		self._aplay_process = None;
		return False;
		
	def WaitWhileSpeaking(self):
		while(self.IsSpeaking()):
			time.sleep(0.1);

	def Speak(self, content, wait=True):
		print("SPEAK: ", content);
		espeak_process = subprocess.Popen(["espeak", self._voice, "-s140", content, "--stdout"], stdout=subprocess.PIPE) 
		self._aplay_process = subprocess.Popen(["aplay", "-D", self._soundcard], stdin=espeak_process.stdout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		if (wait==True):
			self.WaitWhileSpeaking();

	def Release(self):
		if (self._released == False):
			self._released = True;
			print("speech releasing")

			
	def __del__(self):
		self.Release()
			
def exit_handler():
	speechOut.Release()

import atexit

if __name__ == "__main__":
	
		
	pygame.init()
	
	speechOut = SpeechOutput(soundcard="plughw:1", voice="-vmb-de2"); 
	
	atexit.register(exit_handler)
	
	#speechOut.Speak2("Hallo")
	
	speechOut.Speak("Hallo", wait=False)
	time.sleep(3);
	speechOut.Speak("Möchtest Du eine Partie go mit mir spielen?", wait=True);
	speechOut.Speak("Ich habe eine Spielstärke von etwa 5 kyu.", wait=True)
	speechOut.Speak("Hui")
	
	#start_new_thread(speechOut.UpdateEndless(),())
	
	#while True:
	#	speechOut.Speak("Hallo")
	#	time.sleep(2)
	#	print("run")

	#speechOut.ended = True
	
