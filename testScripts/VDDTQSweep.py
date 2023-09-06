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
    # Sweep Parameters
    inputStart  = -50e-9
    inputStop   = 10e-6
    inputSteps  = 2000

    # Physical Setup
    Rin = 100e3


    outDirName = "outputdata/VDDTQSweep" + input("Input the Filename and hit Enter to start the acquisition:") #prompting the user for the directory name
    if not os.path.exists(outDirName):
        os.makedirs(outDirName)

    try:

        # Initialise & Configure the SMU
        SMU = ddf.initialiseSMU()
        ddf.configureVoltSMU(SMU)

        # Initialise & Configure the Scope
        SCOPE = ddf.initialiseDSO6000()
        ddf.configureDSO6000(SCOPE) 

        # Configure the SR1
        VinDC = (IinDC*Rin) + 0.6125
        SR1 = ddf.initialiseSR1()
        SR1chanIDs = configureDCSR1(SR1=SR1, Vinitial=0.6)

        # Creating the input current sweep
        inputSweep = np.linspace(inputStart, inputStop, num=inputSteps)

        # Creating empty output vectors
        freq = np.zeros(inputSweep.shape[0])
        curr = np.zeros(inputSweep.shape[0])

        # Creating the datapoint vector
        dataPoints = np.arange(start=0, stop=inputSweep.size, step=1)


        # Creating the metadata table
        metaTable = [['dataPoint'] + dataPoints.tolist(), ['Vin'] + (inputSweep).tolist(), \
            ['testTime'] + [time.strftime('%H:%M %d/%b/%Y', time.localtime())] * dataPoints.size]

        # Writing the metadata table to a csv file
        filename = '{:s}/metadata.csv'.format(outDirName)
        metaFrame = pa.DataFrame(metaTable)
        metaFrame = metaFrame.transpose()
        metaFrame.to_csv(filename, index=False, header=False)

        # Ensure the PPONG is going
        SMU.write("OUTP1 ON")  # Turning on the channel
        SMU.write("SOUR1:VOLT:LEV 0.996") # Starting a trickle current
        input("Perform a RST, then hit any key to continue...")

        tmp = SMU.query("READ?")
        tmp = SMU.query("READ?")
        tmp = SMU.query("READ?")
        tmp = SMU.query("READ?")
        tmp = SMU.query("READ?")

        for k in dataPoints:
            print("\n\n{:d}/{:d}: Setting the input voltage: {:.4g}V".format(k, inputSweep.size, inputSweep[k]))

            SMU.write("SOUR1:VOLT:LEV {:.12g}".format(inputSweep[k]))
            time.sleep(0.2)

            tmp = SMU.query("READ?")
            time.sleep(0.2)
            tmp = SMU.query("READ?")
            time.sleep(0.1)
            tmp = SMU.query("READ?")   
            while True:
                try:           
                   curr[k] = float(re.findall(r'\x01\x00(.*)\r', tmp)[0])
                except Exception:
                    time.sleep(0.5)
                    tmp = SMU.query("READ?")
                    continue
                break

            freq[k] = float(SCOPE.query("COUN:CURR?"))

            if(freq[k] > 1e9):
                input("Ring stalled. Perform a RST, then hit any key to continue...")
                time.sleep(1)
                freq[k] = float(SCOPE.query("COUN:CURR?"))


        SMU.write("OUTP1 OFF")  # Turning off the channel
        SMU.write("SOUR1:VOLT:LEV 0") # Setting voltage to 0
        

        # Plot the Raw Data
        plt.figure(1)
        plt.plot(inputSweep, freq, '*-')
        plt.xlabel("Input Voltage [V]")
        plt.ylabel("Output Frequency [Hz]")
        plt.grid()

        plt.figure(2)
        plt.plot(inputSweep[16:-1:16], np.diff(freq[0:-1:16])/np.diff(inputSweep[0:-1:16]), label="Diff2 Method")
        plt.plot(inputSweep, freq/inputSweep, label="Division Method")
        plt.grid()
        plt.xlabel("Input Voltage [V]")
        plt.ylabel("Ring Kvco [MHz/V]")
        

    


        outFilename = "vtof"

        np.savetxt("{:s}/{:s}.csv".format(outDirName, outFilename), np.transpose(np.vstack((inputSweep, curr, freq))), fmt="%.12g", delimiter=",")


    except Exception: 
        SMU.write("SOUR1:CURR 0")


