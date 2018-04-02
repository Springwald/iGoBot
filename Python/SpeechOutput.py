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
from MultiProcessing import MultiProcessing

class SpeechOutput(MultiProcessing):

	__keySentencesToSpeak		= MultiProcessing.get_next_key()
	__keySpeaking				= MultiProcessing.get_next_key()
	_released					= False;
	
	## multi process properties START ##
	
	@property
	def sentencesToSpeak(self):
		return self.GetSharedValue(self.__keySentencesToSpeak)
	@sentencesToSpeak.setter
	def sentencesToSpeak(self, value):
		self.SetSharedValue(self.__keySentencesToSpeak, value)
		
	@property
	def speaking(self):
		return self.GetSharedValue(self.__keySpeaking)
	@speaking.setter
	def speaking(self, value):
		self.SetSharedValue(self.__keySpeaking, value)
	
	## multi process properties END ##

	def __init__(self):
		print("speech init")
		super().__init__()
		self.sentencesToSpeak = [] # which sentences are actually speaking
		self.speaking = False 
		super().StartUpdating()

	def Update(self):
		if (self._released == True):
			return;
		sentences = self.sentencesToSpeak
		#print (len(sentences))
		if (len(sentences) > 0):
			nextSentence = sentences[0]
			del sentences[0]
			self.sentencesToSpeak = sentences
			self.speaking = True
			self.__speak(nextSentence, True)
		else:
			self.speaking = False
			time.sleep(1)

	def Speak(self, content):
		self.speaking = True
		sentences = self.sentencesToSpeak
		sentences.append(content)
		self.sentencesToSpeak = sentences

	def __speak(self, content, wait):

		#espeak_process = subprocess.Popen(["espeak", "-vde", "-s130", content, "--stdout"], stdout=subprocess.PIPE) # robotic speech
		espeak_process = subprocess.Popen(["espeak", "-vmb-de6", "-s130", content, "--stdout"], stdout=subprocess.PIPE) # more human speech

		if (wait==True):
			 aplay_process = subprocess.call(["aplay", "-D","plughw:1"], stdin=espeak_process.stdout, stdout=subprocess.PIPE) # soundcard 1
			#aplay_process = subprocess.call(["aplay", "-D","plughw:1"], stdin=espeak_process.stdout, stdout=subprocess.PIPE) # default soundcard
			#aplay_process = subprocess.call(["aplay"], stdin=espeak_process.stdout, stdout=subprocess.PIPE)
		else:
			aplay_process = subprocess.Popen(["aplay", "-D", "sysdefault"], stdin=espeak_process.stdout, stdout=subprocess.PIPE)
			
	def Release(self):
		if (self._released == False):
			self._released = True;
			print("speech releasing")
			super().EndUpdating()
			
	def __del__(self):
		self.Release()
			
def exit_handler():
	speechOut.Release()

import atexit

if __name__ == "__main__":
	
	
	#espeak_process = subprocess.Popen(["espeak", "-vde", "-s100", "Hallo", "--stdout"], stdout=subprocess.PIPE)
	#aplay_process = subprocess.call(["aplay", "-D", "sysdefault"], stdin=espeak_process.stdout, stdout=subprocess.PIPE)
	
	#espeak_process = subprocess.Popen(["espeak", "-vde", "-s100", "Guten Tag", "--stdout"], stdout=subprocess.PIPE)
	#aplay_process = subprocess.call(["aplay", "-D", "sysdefault"], stdin=espeak_process.stdout, stdout=subprocess.PIPE)
		
	pygame.init()
	
	speechOut = SpeechOutput() 
	
	atexit.register(exit_handler)
	
	speechOut.Speak("Hallo")
	while (speechOut.speaking==True):
			time.sleep(1)
	speechOut.Speak("Möchtest Du eine Partie GO mit mir spielen?");
	while (speechOut.speaking==True):
			time.sleep(1)
	speechOut.Speak("Ich habe eine Spielstärke von etwa 5 kyu.")
	while (speechOut.speaking==True):
			time.sleep(1)
	#speechOut.Speak("Hui")
	time.sleep(0.5);
	
	#start_new_thread(speechOut.UpdateEndless(),())
	
	#while True:
	#	speechOut.Speak("Hallo")
	#	time.sleep(2)
	#	print("run")

	speechOut.ended = True
	
