import i2cFunctions as i2c
import dwfconstants as dwfc
import time

if __name__ == "__main__":
    

    # Initialise some variables
    i2cAddress = 0x20   # I2C address of the DUT
    i2cRate = 100e3     # I2C clock frequency
    i2cSCL = 24         # I2C SCL pin (DIO24)
    i2cSDA = 25         # I2C SDA pin (DIO25)

    i2cCLKRSReg = 0x00  # Subaddress of CLK_RS divider control
    i2cPWRCNTLReg = 0x03
    try: 
        # Load the DWF library
        dwfL = i2c.loadDwf()

        # Open the Digital Discovery connection
        dwfH = i2c.openDevice(dwfL)

        # Configure the I2C connection
        nak = i2c.i2cConfig(dwf=dwfL, hdwf=dwfH, RateSet=i2cRate, SCL=i2cSCL, SDA=i2cSDA)

        # First prompt the user to hit RSTB (Automate this using GPIO later)
        input("Press the RSTB button. Hit ENTER when complete")

        # Prompt the user to lock at Fmin
        input("Lock the CLK_RS at the minimum frequency. Hit ENTER when complete")


        
        # Set CLK_RS divider to max value
        nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=i2cCLKRSReg, data=0x0F)
        # Disable the CCRO
        nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=i2cPWRCNTLReg, data=0x00)

        # SRAM Fill Section
        




    except Exception:
        i2c.closeDevice(dwf=dwfL)

    # Close the Digital Discovery Connection
    i2c.closeDevice(dwf=dwfL)



