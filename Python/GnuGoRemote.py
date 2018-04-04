#!/usr/bin/python
#-*-coding:utf-8-*-
#vim: set enc=utf8:

#     #########################
#     # gnu go remote control #
#     #########################
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

from sys import exit as sysexit
from os.path import splitext
import os
import time
from subprocess import Popen, PIPE, STDOUT

class GnuGoRemote():

	_cmdCount = 0;
	_released = False;

	def __init__(self, boardSize):
		self._cmdCount = 0;
		print ("GnuGoRemote - board size: ", boardSize)
		
		cmd = "/usr/games/gnugo"
		self._gnuGoInstance = Popen([cmd , "--mode", "gtp"], stdout=PIPE, stdin=PIPE);
		print(self.SendGnuGoCommand("boardsize " + str(boardSize)));
		print(self.SendGnuGoCommand("clear_board"));

	def SendGnuGoCommand(self, command):
		debug = False
		cmd = str(self._cmdCount).encode() + b' ' + command.encode() + b'\n';
		if debug:
			print (cmd)
		self._gnuGoInstance.stdin.write(cmd)
		self._gnuGoInstance.stdin.flush()
		done = False;
		while(not done):
			line = self._gnuGoInstance.stdout.readline()
			if (line != b'\n'):
				value = line;
				if (value.startswith(b'=' + str(self._cmdCount).encode())):
					done=True;
		self._cmdCount += 1
		valueDecoded = value.decode("utf-8").strip();
		if " " in valueDecoded: 
			check, result = valueDecoded.split(' ')
			return result;
		else:
			return '';
			
	def PlayerPlayWhite(self, fieldAz):
		print("gnuGo: Players put white on ", fieldAz);
		return self.SendGnuGoCommand('play white ' + fieldAz)
		
	def PlayerPlayBlack(self, fieldAz):
		print("gnuGo: Players put black on ", fieldAz);
		return self.SendGnuGoCommand('play black ' + fieldAz)
			
	def AiPlayWhite(self):
		stone = self.SendGnuGoCommand('genmove white')
		print("gnuGo: AI put white on ", stone);
		return stone;
			
	def Release(self):
		if (self._released == False):
			self._released = True;
			print(self.SendGnuGoCommand("quit"));
			print("released gnuGoRemote");

import atexit
		
def exit_handler():
	gnuGo.Release()
	return;

if __name__ == "__main__":
	
	gnuGo =  GnuGoRemote(boardSize=13);
	
	atexit.register(exit_handler)
	
	print(gnuGo.SendGnuGoCommand('genmove white'));
	print(gnuGo.SendGnuGoCommand('genmove white'));
	print(gnuGo.SendGnuGoCommand('genmove black'));
	print(gnuGo.SendGnuGoCommand('genmove white'));
	


 

    
