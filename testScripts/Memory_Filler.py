import i2cFunctions as i2c
import dwfconstants as dwfc
import time


def filler1(): 
    if __name__ == "__main__":
        

        # Initialise some variables
        i2cAddress = 0x20   # I2C address of the DUT
        i2cRate = 100e3     # I2C clock frequency
        i2cSCL = 24         # I2C SCL pin (DIO24)
        i2cSDA = 25         # I2C SDA pin (DIO25)

        i2cCLKRSReg = 0x00  # Subaddress of CLK_RS divider control

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

        global fill_inc, inc7, num
    
        inc7 = 0
        write_num = 0x00    #DATA TO BE FILLED


        while(inc7<=12):
            fill_inc = 0x00
            while(nak.value !=0):  
                    i2c.i2cWrite(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, regW=0x07, write=(0x00+inc7))
                    time.sleep(1.0)

            while(fill_inc < 0x04):
                reg_inc = fill_inc + 0x08
                while(nak.value !=0):  
                    i2c.i2cWrite(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, regW=reg_inc, write=write_num)
                    time.sleep(1.0)

            while(nak.value !=0):  
                    i2c.i2cWrite(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, regW=0x07, write=0x02+inc7)
                    time.sleep(1.0)
            
            inc7 += 4
        
        

    

filler1()