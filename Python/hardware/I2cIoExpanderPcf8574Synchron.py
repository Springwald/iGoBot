#!/usr/bin/env python

import time,sys,os

# insert the directory of this module to the path:
my_file = os.path.abspath(__file__)
my_path ='/'.join(my_file.split('/')[0:-1])
sys.path.insert(0, my_path)
sys.path.insert(0,my_path + "/../libs" )

from PCF8574 import PCF8574


class I2cIoExpanderPcf8574Synchron():

	I2cAdress				= 0x38  #Set the address of the Pcf8574
	_i2c					= None
	_useAsInput				= False

	__int_values			= None
	__key_actual_value		= 0

	def __init__(self, address, useAsInputs = False):
		self._i2c = PCF8574(address, debug=False)
		self._useAsInput = useAsInputs
		if (useAsInputs == True):
			self._i2c.write(0xff)
			self.__read()
			if(self.getByte()==0):
				raise ValueError('received 0 from port ' + str(address) + '. this is unexprected!')
				
	@property
	def _actual_value(self):
		return self.__key_actual_value
		
	@_actual_value.setter
	def _actual_value(self, value):
		self.__key_actual_value = value;
		

	def setByte(self, value):
		self._actual_value = value
		self.__write()

	def getByte(self):
		self.__read();
		return self._actual_value

	def setBit(self,bit, value):
		self._actual_value = self.set_bit_internal(self._actual_value,bit,value)
		self.__write()

	def getBit(self,bit):
		self.__read()
		return self._actual_value&bit == 0

	def __read(self):
		self._actual_value = self._i2c.read()
	
	def __write(self):
		self._i2c.write(self._actual_value)

	def set_bit_internal(self,v, index, x):
		"""Set the index:th bit of v to x, and return the new value."""
		mask = 1 << index
		v &= ~mask
		if x:
			v |= mask
		return v

if __name__ == "__main__":
	i = I2cIoExpanderPcf8574Synchron(0x3e,useAsInputs = True)
	while True:
		a = i.getByte()
		print("read: " +str(a))
		time.sleep(0.5)
