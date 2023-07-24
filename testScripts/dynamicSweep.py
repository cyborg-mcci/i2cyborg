import i2cFunctions as i2c
import dwfconstants as dwfc
import time

if __name__ == "__main__":
     # Initialise some variables
    i2cAddress = 0x20       # I2C address of the DUT
    i2cRate = 100e3         # I2C clock frequency
    i2cSCL = 24             # I2C SCL pin (DIO24)
    i2cSDA = 25             # I2C SDA pin (DIO25)