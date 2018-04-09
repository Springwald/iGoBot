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
from Board import Board


class GnuGoRemote():

	_cmdCount 		= 0;
	_boardSize 		= 0;
	_released 		= False;

	def __init__(self, boardSize):
		self._cmdCount = 0;
		self._boardSize = boardSize;
		print ("GnuGoRemote - board size: ", boardSize)
		
		cmd = "/usr/games/gnugo"
		self._gnuGoInstance = Popen([cmd , "--mode", "gtp"], stdout=PIPE, stdin=PIPE);
		print(self.SendGnuGoCommand("boardsize " + str(boardSize)));
		self.ClearBoard();
		
	def ClearBoard(self):
		print("gnuGo: clear board");
		return self.SendGnuGoCommand('clear_board')
		
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
	
	def GetActualBoard(self):
		return Board.FromStones(boardSize=self._boardSize,  blackStones=self.ListBlackStones(), whiteStones=self.ListWhiteStones());

	def ListBlackStones(self):
		stones = self.SendGnuGoCommand('list_stones black');
		if (stones == ''):
			return [];
		return stones.split(' ');

	def ListWhiteStones(self):
		stones = self.SendGnuGoCommand('list_stones white');
		if (stones == ''):
			return [];
		return stones.split(' ');
	
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
				print("gnuGo raw:", value);
				cmdCheck = b'=' + str(self._cmdCount).encode() + b' ';
				if (value.startswith(cmdCheck)):
					done=True;
					value = value[len(cmdCheck):];
		self._cmdCount += 1
		valueDecoded = value.decode("utf-8").strip();
		result = valueDecoded.strip(' \r\n\t');
		print("gnuGo raw:", result);
		return result;

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
	
	gnuGo =  GnuGoRemote(boardSize=9);
	
	atexit.register(exit_handler)
	
	print(gnuGo.PlayerPlayBlack("A1"));
	print(gnuGo.PlayerPlayBlack("J1"));
	print(gnuGo.PlayerPlayBlack("A8"));
	print(gnuGo.PlayerPlayBlack("J7"));
	print("-" + gnuGo.AiPlayWhite() + "-");
	print(gnuGo.PlayerPlayBlack("C3"));
	print("-" + gnuGo.AiPlayWhite() + "-");
	print(gnuGo.PlayerPlayBlack("C4"));
	print("-" + gnuGo.AiPlayWhite() + "-");
	print(gnuGo.PlayerPlayBlack("C5"));
	print("-" + gnuGo.AiPlayWhite() + "-");
	
	print("black:" ,gnuGo.ListBlackStones());
	print("white:", gnuGo.ListWhiteStones());
	
	from Board import Board;
	board = gnuGo.GetActualBoard();
	board.Print();
	
	#print(gnuGo.SendGnuGoCommand('genmove white'));
#	print(gnuGo.SendGnuGoCommand('genmove black'));
#	print(gnuGo.SendGnuGoCommand('genmove white'));
	


 

    
