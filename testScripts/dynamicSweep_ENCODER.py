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

if __name__ == "__main__":

    # Physical Setup
    Rin = 604e3


    # Stimulation Settings
    F_ref = 1000e6
    f_in = 107002.258301
    IinDC = 6e-6
    AmplStart_Ipk = 1e-9
    AmplStop_Ipk = 5.5e-6
    NoAmplSteps = 401
    
    # Acquisition Settings
    N_samp = 2**17
    acqCLKChan = 0
    edge = 1 # 1 for rising edge triggering, 0 for falling edge triggering

    # Post-Processing Settings
    
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
        VinDC = (IinDC*Rin) + 0.6125
        SR1 = ddf.initialiseSR1()
        SR1chanIDs = ddf.configureSR1(SR1=SR1, f_in=f_in, Voffs=1.2)

        # Calculate T_Q
        T_ref = 1/F_ref
        T_Q = T_ref/66

        # Calculate Voltage Sweep Amplitudes
        AmplStart_Vpk = AmplStart_Ipk * Rin
        AmplStop_Vpk = AmplStop_Ipk * Rin

        # Creating the Amplitude Sweep
        AmplSweep = np.logspace(math.log10(AmplStart_Vpk), math.log10(AmplStop_Vpk), num=NoAmplSteps, base=10.0)

        # Creating the datapoint vector
        dataPoints = np.arange(start=0, stop=NoAmplSteps, step=1)

        # Creating the metadata table
        metaTable = [['dataPoint'] + dataPoints.tolist(), ['Iin_pk'] + (AmplSweep/Rin).tolist(), \
            ['T_Q'] + [T_Q] * dataPoints.size, ['f_in'] + [f_in] * dataPoints.size, \
            ['I_DC'] + [IinDC] * dataPoints.size, ['N_samp'] + [N_samp] * dataPoints.size, \
            ['testTime'] + [time.strftime('%H:%M %d/%b/%Y', time.localtime())] * dataPoints.size]

        # Writing the metadata table to a csv file
        filename = '{:s}/metadata.csv'.format(outDirName)
        metaFrame = pa.DataFrame(metaTable)
        metaFrame = metaFrame.transpose()
        metaFrame.to_csv(filename, index=False, header=False)
        
 

        # Enable the output of the SR1
        SR1.write(":AnlgGen:Ch(0):DC({:d}):Amp {:.12g}".format(SR1chanIDs.get('DC', 0), 1.2))
        SR1.write(":AnlgGen:Ch(0):On True")
        
        # Trying to write the GB amplifier OFF and get the PPONG running
        # running = False
        # while running is not True:
        #     nak = ddf.i2cWrite(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cAFECNTLReg, data=0x01)

        #     nak = ddf.i2cWrite(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cPWRCNTLReg, data=0x00)
        #     nak = ddf.i2cWrite(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cPWRCNTLReg, data=0x02)

        #     if(input("Is the CCO Running? [y/n]:") == "y"):
        #         running = True
            

        input("Hold RSTBCLK, then hit any key to continue...")

        # Resetting the AFE since the SR1 being off will pull PPong into latch
        # nak = ddf.i2cWrite(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cPWRCNTLReg, data=0x00) # Turn off the PPONG
        # nak = ddf.i2cWrite(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cPWRCNTLReg, data=0x00)
        # nak = ddf.i2cWrite(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cPWRCNTLReg, data=0x00)
        # for k in range(1,20):
        #     nak = ddf.i2cWrite(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cPWRCNTLReg, data=0x02) # Turn ON the PPONG
        
        

        sts = ctypes.c_byte()
        rgwSamples = (ctypes.c_uint32 * N_samp)()
        cAvailable = ctypes.c_int()
        cLost = ctypes.c_int()
        cCorrupted = ctypes.c_int()
        cSamples = 0
        fLost = 0
        fCorrupted = 0

        # Performing an initial acquisition to clear the pipes
        ddf.closeDevice(dwf=dwfL) # Closing and re-opening bc it can't go into acq mode after i2c writes?
        dwfH = ddf.openDevice(dwfL)
        nak = ddf.i2cConfig(dwf=dwfL, hdwf=dwfH, RateSet=i2c.i2cRate, SCL=i2c.i2cSCL, SDA=i2c.i2cSDA)
        ddf.acqisitionSetup(dwf=dwfL, hdwf=dwfH, N_samp=N_samp, CLK_Chan=acqCLKChan, edge=1)

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


        for k in dataPoints: 
            print("\n\nSetting the amplitude: {:.4f}uApk which translates to {:.6f}Vpk".format(AmplSweep[k]*1e6/Rin, AmplSweep[k]))

            # Set the SR1 output amplitude
            SR1.write(":AnlgGen:Ch(0):DC({:d}):Amp {:.12g}".format(SR1chanIDs.get('DC', 0), VinDC)) # Updating the DC offset of the function generator if necessary
            SR1.write(":AnlgGen:Ch(0):Sine({:d}):Amp {:.12g} VPP".format(SR1chanIDs.get('Sine', 0), (2*AmplSweep[k]))) # Updating the sine wave amplitude for this element in the sweep
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
        # Disable the output of the SR1
        SR1.write(":AnlgGen:Ch(0):On False")
        SR1.write(":AnlgGen:Ch(0):DC({:d}):Amp {:.12g}".format(SR1chanIDs.get('DC', 0), 1.2)) # Ensure SR1 is at a safe voltage for next time
        SR1.write(":AnlgGen:Ch(0):Sine({:d}):Amp {:.12g} VPP".format(SR1chanIDs.get('Sine', 0), 0))


    

    except Exception:
        ddf.closeDevice(dwf=dwfL)
        # Disable the output of the SR1
        SR1.write(":AnlgGen:Ch(0):On False")
        SR1.write(":AnlgGen:Ch(0):DC({:d}):Amp {:.12g}".format(SR1chanIDs.get('DC', 0), 1.2)) # Ensure SR1 is at a safe voltage for next time
        SR1.write(":AnlgGen:Ch(0):Sine({:d}):Amp {:.12g} VPP".format(SR1chanIDs.get('Sine', 0), 0))
        
        
        
    

    


