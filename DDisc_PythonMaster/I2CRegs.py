import re
import ctypes
import sys
from dwfconstants import *
import time
import i2cFunctions as i2c

#CONFIGURATION
Addr = 0x45            # SLAVE ADDRESS 
RateSet = 100e3        # Clock Rate
i2cSCL = 24            # SCL Pin Set
i2cSDA = 25            # SDA Pin Set

dwf = i2c.loadDwf()     #Loads DWF library for i2c communication
hdwf = i2c.openDevice(dwf)   #Opens DDD and creates a device handle for the device called hdwf
nak = i2c.i2cConfig(dwf, hdwf, RateSet, i2cSCL, i2cSDA)

file = open('shortReg.txt', 'r')   #Command to open the txt file
read = file.readlines()
global inc
inc = 1
length = len(read)

while (inc<length):     # While loop to execute the functions of the regVals file

    print('-----------------------------------------------------------------------')
    
    line = read[inc-1]
    val1 = line[0]

    inc +=1
    
    if val1 == '1':     # WRITE SEQUENCE

        reg_line_Read = read[inc-1]
        reg_number = int(regR[0])
        
        inc +=1

        reginc = 0
        while (reginc < reg_number):
            reginc = reginc+1

            data_line = read[inc-1]
            inc +=1
            hexreg = re.findall(r'[0-9A-Fa-f]+', data_line)   #Finding the registers and data in the text file

            sREG = hexreg[0]         # Coverting string to HEX, and assigning the Regs and data to variables REG and Data
            sData = hexreg[1]
            iREG = int(sREG, 16)
            iData = int(sData, 16)
            REG = hex(iREG)
            Data = hex(iData)

            print("Register: {:04X}\tData:{:04X}".format(REG, Data))
           
            # i2c.i2cWrite(dwf, hdwf, nak, address, reg, data)    #
            nak = i2c.i2cWriteConfirm(dwf, hdwf, nak, Addr, iREG, iData)

    
    elif val1 == '2':   # READ SEQUENCE

        reg_line_read = read[inc-1]
        reg_number = int(regR[0])
            
        inc +=1

        reginc = 0

        while (reginc < reg_number):
                
            reginc = reginc+1

            data_line = read[inc-1]
            inc +=1

            hexreg = re.findall(r'[0-9A-Fa-f]+', data_line)
            sREG = hexreg[0]
            iREG = int(sREG, 16)
            REG = hex(iREG)
            
            # i2c.i2cRead(dwf, hdwf, nak, slave_address, reg)
            dataR, nak = i2c.i2cRead(dwf, hdwf, nak, Addr, iREG)
            print("Register: {:04X}\tData:{:04X}".format(REG, dataR))
        
    elif val1 == '3':   # WAIT SEQUENCE
        
        wait_line = read[inc-1]
        wait_timeS = re.findall(r'\d+', wait_line)
        wait_time = int(wait_timeS[0])

        
        time.sleep(wait_time*1e-6)
        inc = inc+1
    
    else:
        print("Error in text")  
        break