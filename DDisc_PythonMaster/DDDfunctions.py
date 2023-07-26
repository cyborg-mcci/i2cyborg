import ctypes
import sys
import dwfconstants as dwfc
import time
import pyvisa



def loadDwf():                          # TO LOAD DWF 
    if sys.platform.startswith("win"):
        dwf = ctypes.cdll.dwf
    elif sys.platform.startswith("darwin"):
        dwf = ctypes.cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    else:
        dwf = ctypes.cdll.LoadLibrary("libdwf.so")

    version = ctypes.create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("DWF Version: ", version.value)
    return dwf

def closeDevice(dwf):           # TO DSICONNECT DWF DEVICES 
    dwf.FDwfDeviceCloseAll()

def openDevice(dwf):

    hdwf = ctypes.c_int()
    dwf.FDwfDeviceOpen(ctypes.c_int(-1), ctypes.byref(hdwf))

    if hdwf.value == 0:
        print("failed to open device")
        szerr = ctypes.create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        quit()
    # Set the logic voltage to 2.5V
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, ctypes.c_int(0), ctypes.c_int(0), ctypes.c_double(2.5))
    return hdwf

def acqisitionSetup(dwf, hdwf, N_samp, CLK_Chan, edge):
    dwf.FDwfDigitalInAcquisitionModeSet(hdwf, dwfc.acqmodeRecord)  # Setting Record mode
    dwf.FDwfDigitalInDividerSet(hdwf, ctypes.c_int(-1))  # Divider needs to be -1 for sync
    dwf.FDwfDigitalInBufferSizeSet(hdwf, ctypes.c_int(N_samp))
    dwf.FDwfDigitalInSampleFormatSet(hdwf, ctypes.c_int(32))  # Setting to 32 bit per sample format
    dwf.FDwfDigitalInTriggerPositionSet(hdwf, ctypes.c_int(N_samp))  # Setting the number of samples to record for
    dwf.FDwfDigitalInTriggerSet(hdwf, ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(edge << CLK_Chan), ctypes.c_int((not edge) << CLK_Chan))  # Setting the trigger, the syntax here is ...TriggerSet(hdwf, low, high, rising, falling), channel desired is the bit position



def i2cConfig(dwf, hdwf, RateSet, SCL, SDA):        # CONFIGURE DEVICE FOR I2C PROTOCOL


    dwf.FDwfDigitalI2cReset(hdwf)     # Resets the I2C configuration to default value

    nak  = ctypes.c_int()
    dwf.FDwfDigitalI2cClear(hdwf, ctypes.byref(nak))  # Verifies and tries to solve eventual bus lockup. The argument returns true, non-zero value if the bus is free.
    dwf.FDwfDigitalI2cStretchSet(hdwf, ctypes.c_int(0)) # Disabling clock stretching
    dwf.FDwfDigitalI2cRateSet(hdwf, ctypes.c_double(RateSet))  # Sets the data rate.

    dwf.FDwfDigitalI2cSclSet(hdwf, ctypes.c_int(SCL))       # Specifies the DIO channel to use for I2C clock.
    dwf.FDwfDigitalI2cSdaSet(hdwf, ctypes.c_int(SDA))

    dwf.FDwfAnalogIOChannelNodeSet(hdwf, ctypes.c_int(0), ctypes.c_int(0), ctypes.c_double(2.5))  # Sets the voltage level to 2.5 volts 
    dwf.FDwfAnalogIOEnableSet(hdwf, ctypes.c_int(1))

    dwf.FDwfAnalogIOChannelNodeSet(hdwf, ctypes.c_int(0), ctypes.c_int(2), ctypes.c_double(0x0003)) # Enables Pull Up/Down on DIO24 (bit0=1: 1) and DIO25 (bit1=1: 2) to give 0x03
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, ctypes.c_int(0), ctypes.c_int(3), ctypes.c_double(0x0003)) # Sets the DIO24 (bit0) and DIO25 (bit1) to 1 for pull up = 0x03 
    return nak 

def i2cWrite(dwf, hdwf, nak, addr, reg, data):      # I2C WRITE FUNCTION 


    data = [reg, data]
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


def i2cRead(dwf, hdwf, nak, addr, reg):         # I2C READ FUNCTION 


    bufferR = (ctypes.c_ubyte * 1)()

    dwf.FDwfDigitalI2cWriteRead(hdwf, ctypes.c_int(addr << 1), (c_ubyte*1)(reg), ctypes.c_int(1), bufferR, ctypes.c_int(1), ctypes.byref(nak))

    dataR = [int(element) for element in bufferR]


    #print('Data in reg {:02X}: {:02X}'.format(regR, dataR[0])) # Commenting out bc I only want the result to print if it acks
    return dataR[0], nak

def i2cWriteConfirm(dwf, hdwf, nak, addr, reg, data, console=1):     # ROBUST I2C WRITE WHICH CONFIRMS THAT THE RIGHT VALUE WAS WRITTEN 
    readVal = 0xFFFF
    while(readVal != data):
            # Perform a write 
            nak.value = 1
            while(nak.value!=0):
                i2cWrite(dwf=dwf, hdwf=hdwf, nak=nak, addr=addr, reg=reg, data=data)
                #time.sleep(0.05)
            
            # Read back value to confirm
            nak.value = 1
            while(nak.value != 0):
                readVal, nak = i2cRead(dwf=dwf, hdwf=hdwf, nak=nak, addr=addr, reg=reg)
                if(console): # Flag to only print when desired
                    print("nak: {:d}\tReg: {:02X}\tValue: {:02X}".format(nak.value, reg, readVal))
    return nak

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

def initialiseSMU():
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource("USB0::0x0403::0x6001::FTYUXLL3::RAW")
    print(inst.query("*IDN?"))
    return inst

def configureSMU(inst):
    inst.write("*RST")
    #inst.write("*CLR")
    inst.query(":SYST:ERR:ALL?")
    inst.write(":SYST:BEEP:STAT ON")

    inst.write("OUTP1 OFF")  # Turning off the channel

    inst.write("SOUR1:FUNC:MODE curr")  # Sourcing settings
    inst.write("SOUR1:CURR:RANG:AUTO ON")
    inst.write("SOUR1:CURR 0")


    #inst.write(":SENS1:FUNC volt")
    inst.write("SENS1:VOLT:PROT 50") # Measure Settings
    inst.write("SENS1:VOLT:RANG:AUTO ON")

    # inst.write("TRIG:SOUR AINT")


