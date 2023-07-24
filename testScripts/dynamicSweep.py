import i2Constants as i2c
import dwfconstants as dwfc
import time
import DDDfunctions as ddf

if __name__ == "__main__":

    # Physical Setup
    Rin = 10e6


    # Stimulation Settings
    f_in = 100e3
    IinDC = 1e-6
    AmplStart_Ipk = 1e-9
    AmplStop_Ipk = 0.25e-6
    NoAmplSteps = 10
    
    # Acquisition Settings
    N_samp = 262144
    acqCLKChan = 0X00000001
    edge = 1 # 1 for rising edge triggering, 0 for falling edge triggering

    # Post-Processing Settings
    Flock = 200e6
    NBW = 1e6

    # Load the DWF library
    dwfL = ddf.loadDwf()

    # Open the Digital Discovery connection
    dwfH = ddf.openDevice(dwfL)

    # Configure the I2C connection
    nak = ddf.i2cConfig(dwf=dwfL, hdwf=dwfH, RateSet=i2cRate, SCL=i2cSCL, SDA=i2cSDA)

    # Configure the Data Acquisition
    ddf.acqisitionSetup(dwf=dwfL, hdwf=dwfH, N_samp=N_samp, CLK_Chan=acqCLKChan, edge=1)

    # Configure the SR1
    VinDC = (IinDC/Rin) + 0.6125
    SR1 = ddf.initialiseSR1()
    SR1chanIDs = ddf.configureSR1(SR1=SR1, f_in=f_in, Voffs=VinDC)


