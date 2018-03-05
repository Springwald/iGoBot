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

from multiprocessing import Array

class SharedInts:

	_pList					= None
	_key_count				= 0

	#@property
	#def _pDict(self):
	#	if (MultiProcessing.__pDictBackingField == None):
	#		print ("MultiProcessing Manager init!")
	#		mgr	= Manager()
	#		MultiProcessing.__pDictBackingField = mgr.dict()
	#		mgr.Pool()
	#	return MultiProcessing.__pDictBackingField
	
	#@staticmethod
	#def get_list():
	#	if (MultiProcessing._pList == None):
	#		print ("MultiProcessing Manager init!")
	#		#mgr	= Manager()
	#		maxLength = 50
	#		MultiProcessing._pList  =Array('d', maxLength, lock=False)
	#		#MultiProcessing._pList = mgr.list()
	#		#MultiProcessing._pList = []
	#		#mgr.Pool(20)
	#	return MultiProcessing._pList

	def __init__(self, max_length=100):
		self._pList  =Array('i', max_length, lock=True)

	def set_value(self, key, value):
		#print ("set_value '" + str(key) + "'" )
		#key_str = str(key) + ":" + str(id(self))
		self._pList[key] = value

	def get_value(self, key):
		#key_str = str(key) + ":" + str(id(self))
		return self._pList[key]

	def get_next_key(self):
		self._pList[self._key_count] = 0
		self._key_count = self._key_count + 1
		return self._key_count-1

if __name__ == "__main__":
	ints = SharedInts(10)
	ints2 = SharedInts(10)
	
	ints.set_value(0,1)
	ints.set_value(1,2)
	ints.set_value(2,4)
	
	ints2.set_value(0,3)
	ints2.set_value(1,6)
	ints2.set_value(2,9)
	
	print(ints.get_value(0))
	print(ints.get_value(1))
	print(ints.get_value(2))
	
	print(ints2.get_value(0))
	print(ints2.get_value(1))
	print(ints2.get_value(2))

