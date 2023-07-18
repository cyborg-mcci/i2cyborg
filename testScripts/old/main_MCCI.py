import os
import numpy as np
from scipy import signal
import pyvisa
import time
import shutil
from ctypes import *
from dwfconstants import *
import math
import sys
import matplotlib.pyplot as plt



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


def initialiseHdwf(dwf, hdwf, N_samp, CLK_Chan):
    #print("Opening the Device")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == 0:
        print("failed to open device")
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        quit()

    #print("Configuring the Digital Input")
    #print("Putting the device into Record Mode & Configuring")
    dwf.FDwfDigitalInAcquisitionModeSet(hdwf, acqmodeRecord)  # Setting Record mode
    dwf.FDwfDigitalInDividerSet(hdwf, c_int(-1))  # Divider needs to be -1 for sync
    dwf.FDwfDigitalInSampleFormatSet(hdwf, c_int(16))  # Setting to 16 bit per sample format
    dwf.FDwfDigitalInTriggerPositionSet(hdwf, c_int(N_samp))  # Setting the number of samples to record for
    dwf.FDwfDigitalInTriggerSet(hdwf, c_int(0), c_int(0), c_int(edge << CLK_Chan), c_int((not edge) << CLK_Chan))  # Setting the trigger edge to rising, the syntax here is ...TriggerSet(hdwf, low, high, rising, falling), channel desired is the bit position

def initialiseSR1():
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource('TCPIP0::169.254.109.180::INSTR')
    print(inst.query("*IDN?"))
    return inst

def configureSR1(SR1, f_in, Voffs):
    SR1.write("*CLS") # Clears the status Register

    #First ensuring the channels are off before anything blows up
    SR1.write(":AnlgGen:Ch(0):On False") # Disables the output 0
    SR1.write(":AnlgGen:Ch(1):On False") # Disables the output 1

    # Setting the Analog Generator configuration
    SR1.write(":AnlgGen:ConnectorConfig aoUnbalGnd") # Sets the output channels to use the BNC connector
    SR1.write(":AnlgGen:Zout aozBal50Un25") # Sets the output impedance to LowZ
    SR1.write(":AnlgGen:Mono True") # Sets Mono mode, as opposed to stereo mode
    SR1.write(":AnlgGen:SampleRate agHz512k") # Sets the sample rate of the analog generator
    SR1.write(":AnlgGen:BurstMode bmNone") # Ensures burst mode is turned off  

    # Channel 0 configuration
    SR1.write(":AnlgGen:Ch(0):Gain 100 PCT") # Sets the channel gain to 100%
    SR1.write(":AnlgGen:Ch(0):ClearWaveforms") # Clears any existing waveforms in the channel

    # Configuring the DC Offset
    chanID_offs = int(SR1.query(":AnlgGen:Ch(0):AddWaveform? awfDC")) # Create a DC Offset and add it to the channel 0. chanID_offs is the ID of this channel
    SR1.write(":AnlgGen:Ch(0):DC({:d}):Amp {:.12g}".format(chanID_offs, Voffs)) # Sets the DC offset of the offset object on channel 0 to Voffs
    SR1.write(":AnlgGen:Ch(0):DC({:d}):On True".format(chanID_offs)) # Turns on the DC offset object of channel 0

    chanID_sin = int(SR1.query(":AnlgGen:Ch(0):AddWaveform? awfSine")) # Creates a sine wave object on channel 0. chanID_sin is the ID of this channel
    SR1.write(":AnlgGen:Ch(0):Sine({:d}):Amp 0.1 VPP".format(chanID_sin)) # Sets an initial sine amplitude of 100mVpp. This will be swept throughout the test
    SR1.write(":AnlgGen:Ch(0):Sine({:d}):Freq {:.16g} HZ".format(chanID_sin, f_in)) # Sets the frequency of the sine on channel 0. Ensure there's enough precision for coherent sampling
    SR1.write(":AnlgGen:Ch(0):Sine({:d}):on True".format(chanID_sin)) # Turns on the sine object of channel 0

    chanIDs  = { # Creating a dictionary lookup for the DC offset and sin functions to be returned and used elsewhere in the script
        'DC':   chanID_offs,
        'Sine': chanID_sin
    }
    return chanIDs



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Global Parameters for the acquisition
    N_samp = 262144*1
    DDisc_CLK_Chan = 7
    edge = 0  # edge to sample the data on, 1 for rising, 0 for falling
    fs = 1.25e9 / 32
    AmplStart_Ipk = 1.5e-9 # Minimum amplitude for the DS360 yields about Imin = 2nA
    AmplStop_Ipk = 8e-6
    NoAmplSteps = 250
    Ioffs = 0e-6
    #f_in = (419/262144)*(fs)
    f_in = 100.0165939331053e3
    NBW = 1e6



    chanSel = input("Select Channel by typing 0-4: ")

    GainDictionary = {
        'E': 3.38e6,  # EXT CNTL
        '0': 2.3858e6,  # CH0
        '1': 3.3108e6,  # CH1
        '2': 3.3901e6,  # CH2
        '3': 3.3941e6,  # CH3
        '4': 3.4078e6,  # CH4
        'tmp':200e3
    }

    ItoV_Gain = GainDictionary.get(chanSel,3.4e6)
    AmplStart_Vpk = ItoV_Gain * AmplStart_Ipk
    AmplStop_Vpk = ItoV_Gain * AmplStop_Ipk
    Voffs = (0.62+Ioffs*ItoV_Gain)



    SR1 = initialiseSR1()

    SR1_chan_IDs = configureSR1(SR1, f_in=f_in, Voffs=Voffs)


    # Setting initial variables for the DDisc
    hdwf = c_int()
    sts = c_byte()
    rgwSamples = (c_uint16 * N_samp)()
    cAvailable = c_int()
    cLost = c_int()
    cCorrupted = c_int()
    cSamples = 0
    fLost = 0
    fCorrupted = 0




    # Setting up the DDisc
    dwf = loadDwf()
    #initialiseHdwf(dwf, hdwf, N_samp, DDisc_CLK_Chan)
    #dwf.FDwfDigitalInConfigure(hdwf, c_bool(0), c_bool(0))

    # Setting up the current sweep
    #AmplSweep = np.linspace(AmplStart_Vpk, AmplStop_Vpk, NoAmplSteps)
    AmplSweep = np.logspace(math.log10(AmplStart_Vpk), math.log10(AmplStop_Vpk), num=NoAmplSteps, base=10.0) # Logarithmic Sweep

    outDirname = input("Input the Filename and hit Enter to start the acquisition:") #prompting the user for the directory name
    if not os.path.exists(outDirname):
        os.makedirs(outDirname)

    sweepCnt = 0

    #Enable the output of the SR1
    SR1.write(":AnlgGen:Ch(0):On True")

    SNDR = np.zeros(AmplSweep.size)
    SNR = np.zeros(AmplSweep.size)
    THD = np.zeros(AmplSweep.size)

    for k in AmplSweep:
        hdwf = c_int()
        sts = c_byte()
        rgwSamples = (c_uint16 * N_samp)()
        cAvailable = c_int()
        cLost = c_int()
        cCorrupted = c_int()
        cSamples = 0
        fLost = 0
        fCorrupted = 0
        initialiseHdwf(dwf, hdwf, N_samp, DDisc_CLK_Chan)
        sweepCnt+=1

        print("\n\nSetting the amplitude: {:.4f}uApk which translates to {:.6f}Vpk".format(k*1e6/ItoV_Gain, k))
        
        
        SR1.write(":AnlgGen:Ch(0):DC({:d}):Amp {:.12g}".format(SR1_chan_IDs.get('DC', 0), Voffs)) # Updating the DC offset of the function generator if necessary
        SR1.write(":AnlgGen:Ch(0):Sine({:d}):Amp {:.12g} VPP".format(SR1_chan_IDs.get('Sine', 0), (2*k))) # Updating the sine wave amplitude for this element in the sweep
        time.sleep(0.1)

        dwf.FDwfDigitalInConfigure(hdwf, c_bool(1), c_bool(1))

        while cSamples < N_samp:
            dwf.FDwfDigitalInStatus(hdwf, c_int(1), byref(sts))
            if cSamples == 0 and (sts == DwfStateConfig or sts == DwfStatePrefill or sts == DwfStateArmed):
                print("Acquisition not yet started")
                continue

            dwf.FDwfDigitalInStatusRecord(hdwf, byref(cAvailable), byref(cLost), byref(cCorrupted))
            cSamples += cLost.value

            if cLost.value:
                fLost = 1
            if cCorrupted.value:
                fCorrupted = 1
            if cAvailable.value == 0:
                continue
            if cSamples + cAvailable.value > N_samp:
                cAvailable = c_int(N_samp - cSamples)
            dwf.FDwfDigitalInStatusData(hdwf, byref(rgwSamples, 2 * cSamples), c_int(2 * cAvailable.value))
            cSamples += cAvailable.value

        dwf.FDwfDeviceClose(hdwf)

        #print("Acquisition Complete! Progress: {:.2f}%".format(sweepCnt * 100 / NoAmplSteps))
        if fLost:
            print("Samples were lost!")
        if cCorrupted:
            print("Samples could be corrupt! ({:f} of them)".format(cCorrupted.value))

        outFilename = "CHAN_DynamicSweep_{:.6f}uA".format(k*1e6/ItoV_Gain)
        #f = open("{:s}/{:s}.csv".format(outDirname, outFilename), "w")

        raw_output = np.asarray(rgwSamples)
        raw_output = (raw_output & 0b01111111) | (raw_output & 0b100000000) >> 1
        np.savetxt("{:s}/{:s}.csv".format(outDirname, outFilename), raw_output, fmt="%d", delimiter=",")
        #f.write("%s\n" % (raw_output))
        #raw_output = np.zeros(N_samp)
        #k = 0
        #for v in rgwSamples:
        #    b0 = (v & (0b1 << 0)) >> 0
        #    b1 = (v & (0b1 << 1)) >> 1
        #    b2 = (v & (0b1 << 2)) >> 2
        #    b3 = (v & (0b1 << 3)) >> 3
        #    b4 = (v & (0b1 << 4)) >> 4
        #    b5 = (v & (0b1 << 5)) >> 5
        #    b6 = (v & (0b1 << 6)) >> 6
        #    b7 = (v & (0b1 << 7)) >> 7
        #    b8 = (v & (0b1 << 8)) >> 8
            #b9 = (v & (0b1 << 9)) >> 9
            #b10 = (v & (0b1 << 10)) >> 10
            #b11 = (v & (0b1 << 11)) >> 11
            #b12 = (v & (0b1 << 12)) >> 12
            #b13 = (v & (0b1 << 13)) >> 13
            #b14 = (v & (0b1 << 14)) >> 14
            #b15 = (v & (0b1 << 15)) >> 15
            #raw_output[k] = b0*(2**0) + b1*(2**1) + b2*(2**2) + b3*(2**3) + b4*(2**4) + b5*(2**5) + b6*(2**6) + b8*(2**7)
        #    raw_output = b0*(2**0) + b1*(2**1) + b2*(2**2) + b3*(2**3) + b4*(2**4) + b5*(2**5) + b6*(2**6) + b8*(2**7)
         #   f.write("%s\n" % (raw_output))
            #k += 1
        #f.close()

        #fig1 = plt.figure(1)
        #fig1.clear()
        #plt.plot(raw_output, '*-')
        #plt.grid(which='both', axis='both')

        fig2 = plt.figure(2)
        fig2.clear()
        #f, Pxx = signal.periodogram(rgwSamples, fs=32.5e6, window='hamming', nfft=N_samp, detrend='constant',
        #                            return_onesided=True, scaling='density')
        f, Pxx = signal.welch(raw_output, fs=fs, window='blackmanharris', nperseg=32768, noverlap=8192,
                              detrend='constant', return_onesided=True, scaling='density')

        fin_index = np.abs(f - f_in).argmin()

        # Converting from PSD to power per bin
        df = f[2] - f[1]
        Pow_bin = Pxx * df

        # Removing the DC Component
        tmp = np.arange(start=0, stop=5, step=1)
        Pow_DC = sum(Pow_bin[tmp])
        Pow_bin[tmp] = 0

        # Extracting the input signal
        tmp = np.arange(start=-4, stop=4, step=1) + fin_index
        Pow_in = sum(Pow_bin[tmp])
        Pow_bin[tmp] = 0

        # Deleting everything above the NBW
        ind_NBW = np.abs(f - NBW).argmin()
        Pow_bin[ind_NBW:] = 0

         # Removing the weird 980kHz spur
        #ind_SPUR = np.arange(start=-3, stop=3, step=1) + np.abs(f - 980e3).argmin()
        #Pow_bin[ind_SPUR] = 0

        Pow_nd = sum(Pow_bin)

        SNDR[sweepCnt-1] = 10 * np.log10(Pow_in / Pow_nd)

        # Calculating the THD
        f_harm = np.arange(start=2, stop=11, step=1) * f_in
        f_harm_ind = np.zeros(f_harm.size, dtype=int)

        indoffs = np.arange(start=-4, stop=4, step=1)
        Pow_harm = np.zeros(f_harm.size)
        for m in range(0, f_harm.size - 1):
            f_harm_ind[m] = np.abs(f - f_harm[m]).argmin()
            tmp = indoffs + f_harm_ind[m]
            Pow_harm[m] += sum(Pow_bin[tmp])
            Pow_bin[tmp] = 0

        THD[sweepCnt-1] = 10 * np.log10(sum(Pow_harm) / Pow_in)

        Pow_noise = sum(Pow_bin)
        SNR[sweepCnt-1] = 10 * np.log10(Pow_in / Pow_noise)

        print("Iin_pk = {:.4f}uA\t({:.2f}% Complete):\tSNDR = {:.3f}dB\t-THD = {:.3f}dB\tSNR = {:.3f}dB".format(k*1e6/ItoV_Gain, sweepCnt * 100 / NoAmplSteps, SNDR[sweepCnt-1], -THD[sweepCnt-1], SNR[sweepCnt-1]))

        # plt.semilogx(f, 10 * (np.log10(Pxx)) - 10 * (np.log10(Pxx[fin_index])))
        # plt.grid(which='both', axis='both')
        # plt.xlabel('frequency [Hz]')
        # plt.ylabel('PSD [dBc]')
        # plt.show(block=False)
        # plt.pause(0.001)
        

    #Enable the output of the SR1
    SR1.write(":AnlgGen:Ch(0):On False")

    fig3 = plt.figure(3)
    fig3.clear()
    plt.semilogx(AmplSweep*1e6/ItoV_Gain, SNDR, label="SNDR")
    plt.semilogx(AmplSweep*1e6/ItoV_Gain, SNR, label="SNR")
    plt.semilogx(AmplSweep*1e6/ItoV_Gain, -THD, label="-THD")
    plt.grid(which='both', axis='both')
    plt.xlabel('Current [uA]')
    plt.ylabel('[dB]')
    plt.legend()
    plt.show(block=False)


    print("Sweep Complete, Zipping the file")
    shutil.make_archive(outDirname, 'zip', outDirname)
    shutil.rmtree(outDirname)

