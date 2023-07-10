import re
import ctypes
import sys
from dwfconstants import *
import time
import i2cFunctions as i2c

Addr = 0x45            # SLAVE ADDRESS 

dwf = i2c.loadDwf()     #Loads DWF library for i2c communication

hdwf = i2c.openDevice(dwf)   #Opens DDD and creates a device handle for the device called hdwf

# i2c.i2cConfig(dwf, hdwf, RateSet, SCL SDA)
nak = i2c.i2cConfig(dwf, hdwf, 10e3, 24, 25)

file = open('shortReg.txt', 'r')   #Command to open the txt file

read = file.readlines()
global inc
inc = 1
length = len(read)
while (inc<length):     # While loop to execute the functions of the regVals file

    print('-----------------------------------------------------------------------')
    
    line = read[inc-1]
    val1 = line[0]
    
    if val1 == '1':

        regR = read[inc]
        regNum = int(regR[0])
        
        inc = inc+2

        reginc = 0
        while (reginc < regNum):
            inc = inc+1
            reginc = reginc+1

            reg1 = read[inc-2]
            hexreg = re.findall(r'[0-9A-Fa-f]+', reg1)   #Finding the registers and data in the text file

            sREG = hexreg[0]         # Coverting string to HEX, and assigning the Regs and data to variables REG and Data
            sData = hexreg[1]
            iREG = int(sREG, 16)
            iData = int(sData, 16)
            REG = hex(iREG)
            Data = hex(iData)
           
            print("Register:", REG)    # Print the extracted values
            print("Data:    ", Data)
           
            # i2c.i2cWrite(dwf, hdwf, nak, address, reg, data)    #
            nak = i2c.i2cWrite(dwf, hdwf, nak, Addr, iREG, iData)
        
        time.sleep(1e-6)
        inc = inc+2
    
    
    else:
        print("Error in text")  
        break