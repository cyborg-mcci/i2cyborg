import i2Constants as i2c
import dwfconstants as dwfc
import time
import DDDfunctions as ddf
import numpy as np
import math
import os
import ctypes
import matplotlib.pyplot as plt
import pandas as pa
import byteReverse as br
import re

if __name__ == "__main__":

    # Physical Setup
    Rin = 100e3


    # Stimulation Settings
    F_ref = 400e6
    
    # Sweep Parameters
    inputStart  = 0e-9
    inputStop   = 5e-6
    inputSteps  = 2000
    
    # Acquisition Settings
    N_samp = 2**14
    acqCLKChan = 0
    edge = 1 # 1 for rising edge triggering, 0 for falling edge triggering

    # Postprocessing Settings
    outDirName = "outputdata/linearENC/" + input("Input the Filename and hit Enter to start the acquisition:") #prompting the user for the directory name
    if not os.path.exists(outDirName):
        os.makedirs(outDirName)


    try:
        # Load the DWF library
        dwfL = ddf.loadDwf()

        # Open the Digital Discovery connection
        dwfH = ddf.openDevice(dwfL)

        # Configure the I2C connection
        nak = ddf.i2cConfig(dwf=dwfL, hdwf=dwfH, RateSet=i2c.i2cRate, SCL=i2c.i2cSCL, SDA=i2c.i2cSDA)

        # Configure the Data Acquisition
        ddf.acqisitionSetup(dwf=dwfL, hdwf=dwfH, N_samp=N_samp, CLK_Chan=acqCLKChan, edge=1)

        # Configure the SMU
        SMU = ddf.initialiseSMU()
        ddf.configureSMU(SMU)

        # Calculate T_Q
        T_ref = 1/F_ref
        T_Q = T_ref/66

        # Creating the input current sweep
        inputSweep = np.linspace(inputStart, inputStop, num=inputSteps)

        # Creating the datapoint vector
        dataPoints = np.arange(start=0, stop=inputSteps, step=1)

        # Creating the voltage vector
        volt = np.zeros(inputSweep.shape[0])

        # Creating the metadata table
        metaTable = [['dataPoint'] + dataPoints.tolist(), ['Iin'] + (inputSweep).tolist(), \
            ['T_Q'] + [T_Q] * dataPoints.size, \
            ['N_samp'] + [N_samp] * dataPoints.size, \
            ['testTime'] + [time.strftime('%H:%M %d/%b/%Y', time.localtime())] * dataPoints.size]

        # Writing the metadata table to a csv file
        filename = '{:s}/metadata.csv'.format(outDirName)
        metaFrame = pa.DataFrame(metaTable)
        metaFrame = metaFrame.transpose()
        metaFrame.to_csv(filename, index=False, header=False)
        
 

        # Ensure the PPONG is going
        SMU.write("OUTP1 ON")  # Turning on the channel
        SMU.write("SOUR1:CURR:LEV 10e-9") # Starting a trickle current
        input("Perform a RST, then hit any key to continue...")

                

        sts = ctypes.c_byte()
        rgwSamples = (ctypes.c_uint32 * N_samp)()
        cAvailable = ctypes.c_int()
        cLost = ctypes.c_int()
        cCorrupted = ctypes.c_int()
        cSamples = 0
        fLost = 0
        fCorrupted = 0

        

        dwfL.FDwfDigitalInConfigure(dwfH, ctypes.c_bool(0), ctypes.c_bool(1))
        cSamples = 0
        while cSamples < N_samp:
            dwfL.FDwfDigitalInStatus(dwfH, ctypes.c_int(1), ctypes.byref(sts))
            if cSamples == 0 and (sts == dwfc.DwfStateConfig or sts == dwfc.DwfStatePrefill or sts == dwfc.DwfStateArmed):
                print("Acquisition not yet started")
                continue

            dwfL.FDwfDigitalInStatusRecord(dwfH, ctypes.byref(cAvailable), ctypes.byref(cLost), ctypes.byref(cCorrupted))
            cSamples += cLost.value

            if cLost.value:
                fLost = 1
            if cCorrupted.value:
                fCorrupted = 1
            if cAvailable.value == 0:
                continue
            if cSamples + cAvailable.value > N_samp:
                cAvailable = ctypes.c_int(N_samp - cSamples)
            dwfL.FDwfDigitalInStatusData(dwfH, ctypes.byref(rgwSamples,4*cSamples), ctypes.c_int(4 * cAvailable.value))
            cSamples += cAvailable.value

        ppDeadCounter = 0
        for k in dataPoints:
            print("\n\n{:d}/{:d}: Setting the input current: {:.4g}uApk".format(k, inputSteps, inputSweep[k]*1e6))

            SMU.write("SOUR1:CURR:LEV {:g}".format(inputSweep[k]))
            time.sleep(0.3)
            tmp = SMU.query("READ?")

            while True:
                try:           
                   volt[k] = float(re.findall(r'\x01\x00(.*)\r', tmp)[0])
                except Exception:
                    time.sleep(0.75)
                    tmp = SMU.query("READ?")
                    continue
                break

            # Arm the acquisition trigger
            dwfL.FDwfDigitalInConfigure(dwfH, ctypes.c_bool(0), ctypes.c_bool(1))
            cSamples = 0
            while cSamples < N_samp:
                dwfL.FDwfDigitalInStatus(dwfH, ctypes.c_int(1), ctypes.byref(sts))
                if cSamples == 0 and (sts == dwfc.DwfStateConfig or sts == dwfc.DwfStatePrefill or sts == dwfc.DwfStateArmed):
                    print("Acquisition not yet started")
                    continue

                dwfL.FDwfDigitalInStatusRecord(dwfH, ctypes.byref(cAvailable), ctypes.byref(cLost), ctypes.byref(cCorrupted))
                cSamples += cLost.value

                if cLost.value:
                    fLost = 1
                if cCorrupted.value:
                    fCorrupted = 1
                if cAvailable.value == 0:
                    ppDeadCounter+=1
                    if(ppDeadCounter > 100):
                        input("PPONG stalled. Perform a RST, then hit any key to continue...")
                        dwfL.FDwfDigitalInConfigure(dwfH, ctypes.c_bool(0), ctypes.c_bool(1))
                        ppDeadCounter = 0
                        tmp = SMU.query("READ?")
                        while True:
                            try:           
                                volt[k] = float(re.findall(r'\x01\x00(.*)\r', tmp)[0])
                            except Exception:
                                time.sleep(0.75)
                                tmp = SMU.query("READ?")
                                continue
                            break
                    continue
                if cSamples + cAvailable.value > N_samp:
                    ppDeadCounter = 0
                    cAvailable = ctypes.c_int(N_samp - cSamples)

                
                    
                dwfL.FDwfDigitalInStatusData(dwfH, ctypes.byref(rgwSamples,4*cSamples), ctypes.c_int(4 * cAvailable.value))
                cSamples += cAvailable.value
            
            rawOutput = np.asarray(rgwSamples)
            #rawOutput = (rawOutput & 0b0111111111110) + ((rawOutput & 0b1000000000000)>>12) # Using the default low speed cable
            # Using the custom cable
            rawOutputUpper  = br.reverseNibble((rawOutput & 0xF000) >> 12)
            rawOutputMid    = (rawOutput & 0x0F00) >> 8
            rawOutputLower  = br.reverseNibble((rawOutput & 0x0F0) >> 4)
            rawOutput = (rawOutputUpper << 8) + (rawOutputMid << 4) + rawOutputLower

            rawOutput = rawOutput.astype(np.int32)
            outFilename = "{:d}".format(k)
            np.savetxt("{:s}/{:s}.csv".format(outDirName, outFilename), rawOutput, fmt="%d", delimiter=",")

            
            
            
            plt.figure(1)
            plt.plot(rawOutput, '*-')
            plt.grid()
            
            dOutput = np.diff(rawOutput)
            plt.figure(2)
            plt.plot(dOutput, '*'); 
            plt.grid()

            # plt.figure(2)
            # plt.hist(rawOutput, bins=4096)
            # plt.grid()

        ddf.closeDevice(dwf=dwfL)
        # Disable the output of the SMU
        SMU.write("OUTP1 OFF")  # Turning off the channel
        SMU.write("SOUR1:CURR:LEV 0") # Turning off the current

        outFilename = "itov"
        np.savetxt("{:s}/{:s}.csv".format(outDirName, outFilename), np.transpose(np.vstack((inputSweep, volt))), fmt="%.12g", delimiter=",")


    

    except Exception:
        ddf.closeDevice(dwf=dwfL)
        # Disable the output of the SMU
        SMU.write("OUTP1 OFF")  # Turning off the channel
        SMU.write("SOUR1:CURR:LEV 0") # Turning off the current
        
        
        
    

    


