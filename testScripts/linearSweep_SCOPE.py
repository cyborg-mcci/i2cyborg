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


    outDirName = "outputdata/linearSCOPE/" + input("Input the Filename and hit Enter to start the acquisition:") #prompting the user for the directory name
    if not os.path.exists(outDirName):
        os.makedirs(outDirName)

    try:

        # Initialise & Configure the SMU
        SMU = ddf.initialiseSMU()
        ddf.configureSMU(SMU)

        # Initialise & Configure the Scope
        SCOPE = ddf.initialiseDSO6000()
        ddf.configureDSO6000(SCOPE, counterChan=2) 

        # Creating the input current sweep
        inputSweep = np.linspace(inputStart, inputStop, num=inputSteps)

        # Creating empty output vectors
        freq = np.zeros(inputSweep.shape[0])
        volt = np.zeros(inputSweep.shape[0])

        # Creating the datapoint vector
        dataPoints = np.arange(start=0, stop=inputSteps, step=1)


        # Creating the metadata table
        metaTable = [['dataPoint'] + dataPoints.tolist(), ['Iin'] + (inputSweep).tolist(), \
            ['R_in'] + [Rin] * dataPoints.size, \
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


        for k in dataPoints:
            print("\n\n{:d}/{:d}: Setting the input current: {:.4g}uApk".format(k, inputSteps, inputSweep[k]*1e6))

            SMU.write("SOUR1:CURR:LEV {:.12g}".format(inputSweep[k]))
            time.sleep(0.5)
            tmp = SMU.query("READ?")

            while True:
                try:           
                   volt[k] = float(re.findall(r'\x01\x00(.*)\r', tmp)[0])
                except Exception:
                    time.sleep(0.75)
                    tmp = SMU.query("READ?")
                    continue
                break

            freq[k] = float(SCOPE.query("COUN:CURR?"))

            if(freq[k] > 1e9):
                input("Ring stalled. Perform a RST, then hit any key to continue...")
                time.sleep(1)
                freq[k] = float(SCOPE.query("COUN:CURR?"))
                tmp = SMU.query("READ?")
                while True:
                    try:           
                        volt[k] = float(re.findall(r'\x01\x00(.*)\r', tmp)[0])
                    except Exception:
                        time.sleep(0.5)
                        tmp = SMU.query("READ?")
                        time.sleep(0.1)
                        tmp = SMU.query("READ?")
                        time.sleep(0.1)
                        tmp = SMU.query("READ?")
                        continue
                    break


        SMU.write("OUTP1 OFF")  # Turning off the channel
        SMU.write("SOUR1:CURR:LEV 0") # Turning off the current
        

        # Plot the Raw Data
        plt.figure(1)
        plt.plot(inputSweep, freq, '*-')
        plt.xlabel("Input Current [A]")
        plt.ylabel("PPONG Frequency [Hz]")
        plt.grid()

        plt.figure(2)
        plt.plot(inputSweep[16:-1:16], np.diff(freq[0:-1:16])/np.diff(inputSweep[0:-1:16]), label="Diff2 Method")
        plt.plot(inputSweep, freq/inputSweep, label="Division Method")
        plt.grid()
        plt.xlabel("Input Current [A]")
        plt.ylabel("PPONG Kcco [MHz/uA]")

        plt.figure(3)
        plt.plot(inputSweep, volt, '-*', label="Stimulus")
        plt.plot(inputSweep, volt-inputSweep*Rin, label="Interpolated FVF Vin")
        plt.grid()
        plt.xlabel("Input Current [A]")
        plt.ylabel("Voltage [V]")
        

    


        outFilename = "itov"

        np.savetxt("{:s}/{:s}.csv".format(outDirName, outFilename), np.transpose(np.vstack((inputSweep, volt, freq))), fmt="%.12g", delimiter=",")


    except Exception: 
        SMU.write("SOUR1:CURR 0")


