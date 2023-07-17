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

    
def openDevice(dwf):

    hdwf = c_int()
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == 0:
        print("failed to open device")
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        quit()
    # Set the logic voltage to 2.5V
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, 0, 0, c_double(2.5))
    return hdwf

def closeDevice(dwf):
    dwf.FDwfDeviceCloseAll()



def i2cConfig(dwf, hdwf, RateSet, SCL, SDA):


    dwf.FDwfDigitalI2cReset(hdwf)     # Resets the I2C configuration to default value

    nak  = ctypes.c_int()
    dwf.FDwfDigitalI2cClear(hdwf, ctypes.byref(nak))  # Verifies and tries to solve eventual bus lockup. The argument returns true, non-zero value if the bus is free.
    dwf.FDwfDigitalI2cStretchSet(hdwf, ctypes.c_int(0)) # Disabling clock stretching
    dwf.FDwfDigitalI2cRateSet(hdwf, ctypes.c_double(RateSet))  # Sets the data rate.

    dwf.FDwfDigitalI2cSclSet(hdwf, ctypes.c_int(SCL))       # Specifies the DIO channel to use for I2C clock.
    dwf.FDwfDigitalI2cSdaSet(hdwf, ctypes.c_int(SDA))

    dwf.FDwfAnalogIOChannelNodeSet(hdwf, ctypes.c_int(0), ctypes.c_int(0), ctypes.c_double(2.5))  # Sets the voltage level to 2.5 volts 
    dwf.FDwfAnalogIOEnableSet(hdwf, c_int(1))

    dwf.FDwfAnalogIOChannelNodeSet(hdwf, ctypes.c_int(0), ctypes.c_int(2), ctypes.c_double(0x0003)) # Enables Pull Up/Down on DIO24 (bit0=1: 1) and DIO25 (bit1=1: 2) to give 0x03
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, ctypes.c_int(0), ctypes.c_int(3), ctypes.c_double(0x0003)) # Sets the DIO24 (bit0) and DIO25 (bit1) to 1 for pull up = 0x03 
   
    

    return nak 

def i2cWrite(dwf, hdwf, nak, addr, regW, write):


    data = [regW, write]
    bufferW = (ctypes.c_ubyte * len(data))()
    for index in range(0, len(bufferW)):
        bufferW[index] = ctypes.c_ubyte(data[index])


    dwf.FDwfDigitalI2cWrite(hdwf, ctypes.c_int(addr<<1), bufferW, ctypes.c_int(len(data)), ctypes.byref(nak)) 

    nak_count = 0
    if (nak !=0):
        nak_count +=1
        if (nak_count>15):
            print("NAK COUNT OVERFLOW")

    return nak


def i2cRead(dwf, hdwf, nak, addr, regR):


    bufferR = (ctypes.c_ubyte * 1)()

    dwf.FDwfDigitalI2cWriteRead(hdwf, ctypes.c_int(addr << 1), (c_ubyte*1)(regR), ctypes.c_int(1), bufferR, ctypes.c_int(1), ctypes.byref(nak))

    dataR = [int(element) for element in bufferR]


    #print('Data in reg {:02X}: {:02X}'.format(regR, dataR[0])) # Commenting out bc I only want the result to print if it acks
    return dataR[0], nak

def i2cWriteConfirm(dwf, hdwf, nak, addr, reg, data):
    readVal = 0xFFFF
    while(readVal != data):
            # Perform a CLK_RS Clock divider write to slow the output clock
            nak.value = 1
            while(nak.value!=0):
                i2cWrite(dwf=dwf, hdwf=hdwf, nak=nak, addr=addr, regW=reg, write=data)
                time.sleep(0.1)
            
            # Read back the CLK_RS value to confirm
            nak.value = 1
            while(nak.value != 0):
                readVal, nak = i2cRead(dwf=dwf, hdwf=hdwf, nak=nak, addr=addr, regR=reg)
                print("nak: {:d}\tReg: {:02X}\tValue: {:02X}".format(nak.value, reg, readVal))
    return nak
        
            
    
#loadDwf()

#openDevice()

#i2cConfig(10e3, 24, 25)