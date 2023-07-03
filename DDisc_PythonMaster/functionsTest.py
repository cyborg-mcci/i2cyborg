import ctypes
import sys
from dwfconstants import *
import time
import i2cFunctions as i2c

dwf = i2c.loadDwf()

hdwf = i2c.openDevice(dwf)

nak = i2c.i2cConfig(dwf, hdwf, 10e3, 24, 25)


nak = i2c.i2cWrite(dwf, hdwf, nak, 0x45, 0x00, 0xab)
nak = i2c.i2cWrite(dwf, hdwf, nak,0x45, 0x01, 0x00)
nak = i2c.i2cWrite(dwf, hdwf, nak,0x45, 0x02, 0xbb)
nak = i2c.i2cWrite(dwf, hdwf, nak,0x45, 0x03, 0x31)

dataR, nak = i2c.i2cRead(dwf, hdwf, nak, 0x45, 0x00)
dataR, nak = i2c.i2cRead(dwf, hdwf, nak,0x45, 0x01)
dataR, nak = i2c.i2cRead(dwf, hdwf, nak,0x45, 0x02)
dataR, nak = i2c.i2cRead(dwf, hdwf, nak,0x45, 0x03)


