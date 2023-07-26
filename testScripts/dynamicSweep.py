import i2Constants as i2c
import dwfconstants as dwfc
import time
import DDDfunctions as ddf
import numpy as np
import math
import os
import ctypes
import matplotlib.pyplot as plt

if __name__ == "__main__":

    # Physical Setup
    Rin = 10e6


    # Stimulation Settings
    f_in = 100e3
    IinDC = 1e-6
    AmplStart_Ipk = 1e-9
    AmplStop_Ipk = 0.25e-6
    NoAmplSteps = 100
    
    # Acquisition Settings
    N_samp = 262144
    acqCLKChan = 0
    edge = 1 # 1 for rising edge triggering, 0 for falling edge triggering

    # Post-Processing Settings
    Flock = 200e6
    NBW = 1e6
    outDirName = "outputdata/" + input("Input the Filename and hit Enter to start the acquisition:") #prompting the user for the directory name
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

        # Configure the SR1
        VinDC = (IinDC/Rin) + 0.6125
        SR1 = ddf.initialiseSR1()
        SR1chanIDs = ddf.configureSR1(SR1=SR1, f_in=f_in, Voffs=VinDC)

        # Calculate Voltage Sweep Amplitudes
        AmplStart_Vpk = AmplStart_Ipk * Rin
        AmplStop_Vpk = AmplStop_Ipk * Rin

        # Creating the Amplitude Sweep
        AmplSweep = np.logspace(math.log10(AmplStart_Vpk), math.log10(AmplStop_Vpk), num=NoAmplSteps, base=10.0)
        sweepCnt = 0

        # Enable the output of the SR1
        SR1.write(":AnlgGen:Ch(0):On True")

        # Creating empty variables to be filled by the loop
        SNDR = np.zeros(AmplSweep.size)
        SNR = np.zeros(AmplSweep.size)
        THD = np.zeros(AmplSweep.size)

        sts = ctypes.c_byte()
        rgwSamples = (ctypes.c_uint32 * N_samp)()
        cAvailable = ctypes.c_int()
        cLost = ctypes.c_int()
        cCorrupted = ctypes.c_int()
        cSamples = 0
        fLost = 0
        fCorrupted = 0

        # Performing an initial acquisition to clear the pipes
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


        for k in AmplSweep: 
            sweepCnt +=1
            print("\n\nSetting the amplitude: {:.4f}uApk which translates to {:.6f}Vpk".format(k*1e6/Rin, k))

            # Set the SR1 output amplitude
            SR1.write(":AnlgGen:Ch(0):DC({:d}):Amp {:.12g}".format(SR1chanIDs.get('DC', 0), VinDC)) # Updating the DC offset of the function generator if necessary
            SR1.write(":AnlgGen:Ch(0):Sine({:d}):Amp {:.12g} VPP".format(SR1chanIDs.get('Sine', 0), (2*k))) # Updating the sine wave amplitude for this element in the sweep
            time.sleep(0.1)

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
                    continue
                if cSamples + cAvailable.value > N_samp:
                    cAvailable = ctypes.c_int(N_samp - cSamples)
                dwfL.FDwfDigitalInStatusData(dwfH, ctypes.byref(rgwSamples,4*cSamples), ctypes.c_int(4 * cAvailable.value))
                cSamples += cAvailable.value
            
            rawOutput = np.asarray(rgwSamples)
            #rawOutput = (rawOutput & 0b0000000000001)
            rawOutput = (rawOutput & 0b0111111111110) + ((rawOutput & 0b1000000000000)>>12)
            rawOutput = rawOutput.astype(np.int32)
            outFilename = "CHAN_DynamicSweep_{:.6f}uA".format(k*1e6/Rin)
            np.savetxt("{:s}/{:s}.csv".format(outDirName, outFilename), rawOutput, fmt="%d", delimiter=",")
            
            
            plt.figure(1)
            plt.plot(rawOutput, '*-')
            plt.grid()
            
            dOutput = np.diff(rawOutput)
            plt.figure(2)
            plt.plot(dOutput, '*'); plt.grid()

            # plt.figure(2)
            # plt.hist(rawOutput, bins=4096)
            # plt.grid()

        ddf.closeDevice(dwf=dwfL)


    

    except Exception:
        ddf.closeDevice(dwf=dwfL)
        
        
        
    

    


