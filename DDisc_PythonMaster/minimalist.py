import ctypes
import sys
from dwfconstants import *
import time

def loadDwf():
    if sys.platform.startswith("win"):
        dwf = cdll.dwf
    elif sys.platform.startswith("darwin"):
        dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    else:
        dwf = cdll.LoadLibrary("libdwf.so")

    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("DWF Version: ", version.value)
    return dwf


#device_data = device.open()         # WF_SDK file to get the device handle and connect to the DDD

def minimalist():

    dwf = loadDwf()

    hdwf = c_int()
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == 0:
        print("failed to open device")
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        quit()


    dwf.FDwfDigitalI2cReset(hdwf)     # Resets the I2C configuration to default value

    nak = ctypes.c_int()
    dwf.FDwfDigitalI2cClear(hdwf, ctypes.byref(nak))  # Verifies and tries to solve eventual bus lockup. The argument returns true, non-zero value if the bus is free.

    dwf.FDwfDigitalI2cRateSet(hdwf, ctypes.c_double(10e3))  # Sets the data rate.

    dwf.FDwfDigitalI2cSclSet(hdwf, ctypes.c_int(24))       # Specifies the DIO channel to use for I2C clock.
    dwf.FDwfDigitalI2cSdaSet(hdwf, ctypes.c_int(25))

    data = [0x02, 0xaf]
    bufferW = (ctypes.c_ubyte * len(data))()
    for index in range(0, len(bufferW)):
        bufferW[index] = ctypes.c_ubyte(data[index])


    dwf.FDwfDigitalI2cWrite(hdwf, ctypes.c_int(0x45<<1), bufferW, ctypes.c_int(len(data)), ctypes.byref(nak)) 

    time.sleep(2)

    bufferR = (ctypes.c_ubyte * 1)()


    dwf.FDwfDigitalI2cWriteRead(hdwf, ctypes.c_int(0x45 << 1), (c_ubyte*1)(2), ctypes.c_int(1), bufferR, ctypes.c_int(1), ctypes.byref(nak))

    dataR = [int(element) for element in bufferR]

    print("Data: ", dataR)


    #device.close(device_data)
    dwf.FDwfDeviceClose(hdwf)

minimalist()
