import i2cFunctions as i2c
import dwfconstants as dwfc

if __name__ == "__main__":
    

    # Initialise some variables
    i2cAddress = 0x20   # I2C address of the DUT
    i2cRate = 400e3     # I2C clock frequency
    i2cSCL = 24            # I2C SCL pin (DIO24)
    i2cSDA = 25            # I2C SDA pin (DIO25)

    # Load the DWF library
    dwfL = i2c.loadDwf()

    # Open the Digital Discovery connection
    dwfH = i2c.openDevice(dwfL)

    # Configure the I2C connection
    nak = i2c.i2cConfig(dwf=dwfL, hdwf=dwfH, RateSet=i2cRate, SCL=i2cSCL, SDA=i2cSDA)

    # 

    # Close the Digital Discovery Connection
    



