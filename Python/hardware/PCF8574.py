
"""
Interface for a PCF8475 I2C IO Expander
Copyright 2014 Matt Sieker
"""

import smbus
import RPi.GPIO as GPIO
import time

class PCF8574(object):
    """
    Interfaces with a PCF8574 I2C IO Expander
    """
    @staticmethod
    def get_pi_revision():
        """Gets the version number of the Raspberry Pi board"""
        # Courtesy quick2wire-python-api
        # https://github.com/quick2wire/quick2wire-python-api
        # Updated revision info from: http://elinux.org/RPi_HardwareHistory#Board_Revision_History
        try:
            with open('/proc/cpuinfo', 'r') as cpuinfo:
                for line in cpuinfo:
                    if line.startswith('Revision'):
                        return 1 if line.rstrip()[-1] in ['2', '3'] else 2
        except:
            return 0

    @staticmethod
    def get_pi_bus_number():
        """Gets the I2C bus number for a raspbery pi version"""
        return 1
        return 1 if PCF8574.get_pi_revision() > 1 else 0

    @staticmethod
    def hex2(value):
        """Formats a hex byte"""
        return "0x%02x"%(value&0xff)

    def __init__(self, address, busnum=-1, debug=False):
        """Creates a new instance of the PCF8574 class and initializes the I2C bus"""
        self.address = address
        self.debug = debug

        self.int_gpio = None
        self.int_callback = None
        self.bounce_time = None

        # pylint: disable=no-member
        self.bus = smbus.SMBus(busnum if busnum >= 0 else PCF8574.get_pi_bus_number())
        # pylint: enable=no-member

    def __del__(self):
        if self.int_gpio != None and self.int_callback != None:
            # pylint: disable=no-member
            GPIO.cleanup()
            # pylint: enable=no-member

    def __callback_handler(self, channel):
        """
        Handles a GPIO callback, reads from the chip, and passes it on to the
        provided callback method
        """
        if self.debug:
            print ('got callback on {0}'.format(channel))
        value = self.read()
        self.int_callback(value)

    def add_interrupt(self, gpio, callback, bounce_time=25):
        """Enables a GPIO interrupt pin for the /INT line"""
        self.int_gpio = gpio
        self.int_callback = callback
        self.bounce_time = bounce_time

        if self.debug:
            print ("pcf8574: setting up interrput on GPIO{0}".format(self.int_gpio))

        # pylint: disable=no-member
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.int_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.int_gpio, GPIO.FALLING,
                              callback=self.__callback_handler,
                              bouncetime=self.bounce_time)
        # pylint: enable=no-member
        print("hu")

    def write(self, value):
        """Write a byte to the I2C bus"""
        self.bus.write_byte(self.address, value)
        time.sleep(0.01)  # Wait for device to actually settle down
        if self.debug:
            print ("pcf8574: Wrote %s to 0x%02X" % (PCF8574.hex2(value), self.address))

    def read(self):
        """Return a byte read from the I2C bus"""

        result = self.bus.read_byte(self.address)
        if self.debug:
            print ("pcf8574: Reading 0x%02X returned %s" % (self.address, PCF8574.hex2(result)))
        return result

if __name__ == '__main__':
	import time

	def int_callback(value):
		"""Sample Callback"""
		print ('button state {0:b}'.format(value))

	dev = PCF8574(0x3e)
	btns = PCF8574(0x38, debug=True)
	btns.add_interrupt(26, int_callback)
	print (btns.read())
	btns.write(0x00)
	print (btns.read())
	time.sleep(1)
	btns.write(0xff)
	print (btns.read())
	while True:
		#for i in range(0, 15):
			# dev.write(~i)
			
			#print (btns.read())
			#btns.write(0x00)
			#print (btns.read())
			#time.sleep(1)
			btns.write(0xff)
			print (btns.read())
			time.sleep(0.5)
