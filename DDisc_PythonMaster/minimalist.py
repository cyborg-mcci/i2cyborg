from WF_SDK import device, supplies     
import ctypes
from dwfconstants import *

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

hdwf = c_int()
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

#device_data = device.open()         # WF_SDK file to get the device handle and connect to the DDD

def minimalist(device_data):

    dwf.FDwfDigitalI2cReset(device_data.handle)     # Resets the I2C configuration to default value

    nak = ctypes.c_int()
    dwf.FDwfDigitalI2cClear(device_data.handle, ctypes.byref(nak))  # Verifies and tries to solve eventual bus lockup. The argument returns true, non-zero value if the bus is free.

    dwf.FDwfDigitalI2cRateSet(device_data.handle, ctypes.c_double(10e3))  # Sets the data rate.

    dwf.FDwfDigitalI2cSclSet(device_data.handle, ctypes.c_int(24))       # Specifies the DIO channel to use for I2C clock.
    dwf.FDwfDigitalI2cSdaSet(device_data.handle, ctypes.c_int(25))

    data = [0x02, 0xaa, 0xff]
    buffer = (ctypes.c_ubyte * len(data))()
    for index in range(0, len(buffer)):
        buffer[index] = ctypes.c_ubyte(data[index])


    dwf.FDwfDigitalI2cWrite(device_data.handle, ctypes.c_int(0x45<<1), buffer, ctypes.c_int(len(data)), ctypes.byref(nak)) 

    #device.close(device_data)
    dwf.FDwfDeviceClose(hdwf)

minimalist(device_data)
