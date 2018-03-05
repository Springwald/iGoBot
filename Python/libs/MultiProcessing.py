#!/usr/bin/env python

#     ####################################
#     # abstract multi processing module #
#     ####################################
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

#from psutil import *
from multiprocessing import Process, Manager, Value, Array
from multiprocessing import Pool, Array, Process
from SharedInts import SharedInts
import itertools
import os


class MultiProcessing:

	_processName			= "undefined"

	_pList					= None
	_process				= None
	_id						= None
	
	__shared_ints_mp__		= None
	__ended_int__			= 0
	
	_key_count				= 0
	_prio					= 0 # 0 normal, -20 high, 20 low priority

	#@property
	#def _pList(self):
	#	if (MultiProcessing.__pListBackingField == None):
	#		print ("MultiProcessing Manager init!")
	#		mgr	= Manager()
	#		MultiProcessing.__pListBackingField = mgr.list()
	#		mgr.Pool()
	#	return MultiProcessing.__pListBackingField
	
	@staticmethod
	def get_list():
		if (MultiProcessing._pList == None):
			print ("MultiProcessing Manager init!")
			mgr	= Manager()
			#maxLength = 50
			#MultiProcessing._pList  =Array('d', maxLength, lock=False)
			MultiProcessing._pList = mgr.list()
			#MultiProcessing._pList = []
			mgr.Pool()
		return MultiProcessing._pList
	
	@staticmethod
	def get_next_key():
		MultiProcessing._key_count = MultiProcessing._key_count + 1
		MultiProcessing.get_list().append(None)
		return MultiProcessing._key_count-1

	@property
	def updating_ended(self):
		#print(self.__shared_ints__.get_value(self.__ended_int__))
		return self.__shared_ints_mp__.get_value(self.__ended_int__)==1
		
	@updating_ended.setter
	def updating_ended(self, value):
		#print(value)
		if (value==True):
			self.__shared_ints_mp__.set_value(self.__ended_int__,1)
		else:
			self.__shared_ints_mp__.set_value(self.__ended_int__,0)

	def __init__(self, prio = 0):
		#mgr	= Manager()
		#self._pDict = mgr.dict()
		#mgr.Pool()
		
		self.__shared_ints_mp__	= SharedInts(max_length=1)
		self.__ended_int__		= self.__shared_ints_mp__.get_next_key()
	
		self._prio = prio
		print ("init " + self._processName + " - ID " + str(id(self)))
		self.updating_ended = False

	def StartUpdating(self):
		#print ("StartUpdating " + self._processName + " - ID " + str(id(self)))
		self.updating_ended = False
		self._process = Process(target=self.UpdateEndless, args = ())
		self._process.nice = self._prio # -20 high prio, 20 low prio
		self._process.start()
		self._process.nice = self._prio # -20 high prio, 20 low prio

	def SetSharedValue(self, key, value):
		#key = str(key) + str(id(self)) # str(self.__id)
		#print(key)
		self.get_list()[key] = value
		#print(key)
		#MultiProcessing.get_list()[key] = value

	def GetSharedValue(self, key):
		#key = str(key) + str(id(self)) #str(self.__id)
		return self.get_list()[key]
		#return MultiProcessing.get_list()[key]

	def UpdateEndless(self):
		while self.updating_ended == False:
			#print ("Update endless: " + self._processName)
			self.Update()
			
	def EndUpdating(self):
		print ("EndUpdating " + self._processName + " - ID " + str(id(self)))
		self.updating_ended = True

if __name__ == "__main__":
	print("no tests for abstract class multiprocessing available")

