import i2cFunctions as i2c
import dwfconstants as dwfc
import time

if __name__ == "__main__":
    

    # Initialise some variables
    i2cAddress = 0x20   # I2C address of the DUT
    i2cRate = 400e3     # I2C clock frequency
    i2cSCL = 24         # I2C SCL pin (DIO24)
    i2cSDA = 25         # I2C SDA pin (DIO25)

    i2cCLKRSReg = 0x00  # Subaddress of CLK_RS divider control
    i2cPWRCNTLReg = 0x03

    # SRAM_CNTL Reg, Masks & Shifts
    SRAM_CNTL_REG = 0x07
    SRAM_CNTL_ZM0_ENN_MASK =    0b10000000
    SRAM_CNTL_ZM1_ENN_MASK =    0b01000000
    SRAM_CNTL_ZM2_ENN_MASK =    0b00100000
    SRAM_CNTL_ZM3_ENN_MASK =    0b00010000
    SRAM_CNTL_SRAM_SEL_MASK =   0b00001100
    SRAM_CNTL_WR_MASK =         0b00000010
    SRAM_CNTL_RD_MASK =         0b00000001
    SRAM_CNTL_ZM0_ENN_SHIFT =   0x07
    SRAM_CNTL_ZM1_ENN_SHIFT =   0x06
    SRAM_CNTL_ZM2_ENN_SHIFT =   0x05
    SRAM_CNTL_ZM3_ENN_SHIFT =   0x04
    SRAM_CNTL_SRAM_SEL_SHIFT =  0x02
    SRAM_CNTL_WR_SHIFT =        0x01
    SRAM_CNTL_RD_SHIFT =        0x00

    # SRAM ADDR Regs
    SRAM_ADDR_MSB = 0x08
    SRAM_ADDR_LSB = 0x09
    SRAM_ADDR_MSB_MASK = 0x0F
    SRAM_ADDR_LSB_MASK = 0xFF
    SRAM_ADDR_MSB_SHIFT = 0x00
    SRAM_ADDR_LSB_SHIFT = 0x00
    
    SRAM_ADDR_MSB_DATAMASK = 0x0F00
    SRAM_ADDR_LSB_DATAMASK = 0x00FF
    SRAM_ADDR_MSB_DATASHIFT = 0x08
    SRAM_ADDR_LSB_DATASHIFT = 0x00

    # SRAM WDATA Regs
    SRAM_WDATA_MSB = 0x0A
    SRAM_WDATA_LSB = 0x0B
    SRAM_WDATA_MSB_MASK = 0xFF
    SRAM_WDATA_LSB_MASK = 0xFF
    SRAM_WDATA_MSB_SHIFT = 0x00
    SRAM_WDATA_LSB_SHIFT = 0x00

    SRAM_WDATA_MSB_DATAMASK = 0xFF00
    SRAM_WDATA_LSB_DATAMASK = 0x00FF
    SRAM_WDATA_MSB_DATASHIFT = 0x08
    SRAM_WDATA_LSB_DATASHIFT = 0x00

    # SRAM RDATA Regs
    SRAM_RDATA_MSB = 0x18
    SRAM_RDATA_LSB = 0x19
    SRAM_RDATA_MSB_DATAMASK = 0xFF00
    SRAM_RDATA_LSB_DATAMASK = 0x00FF
    SRAM_RDATA_MSB_DATASHIFT = 0x08
    SRAM_RDATA_LSB_DATASHIFT = 0x00



    
    


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
        #nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=i2cCLKRSReg, data=0x0F)
        # Disable the CCRO
        #nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=i2cPWRCNTLReg, data=0x00)
        # Disable the aux output pins


        # SRAM Fill Section
        SRAM_SEL_LIST = [0b00, 0b01, 0b10, 0b11]
        for SRAM_SEL in SRAM_SEL_LIST:
            
            ZM0_ENN = 0
            ZM1_ENN = 0
            ZM2_ENN = 0
            ZM3_ENN = 0
            # Setting the initial SRAM_CNTL write for the loop
            CNTL_WRITE_DEFAULT =  ( SRAM_CNTL_ZM0_ENN_MASK & (ZM0_ENN<<SRAM_CNTL_ZM0_ENN_SHIFT) )         \
                                | ( SRAM_CNTL_ZM1_ENN_MASK & (ZM1_ENN<<SRAM_CNTL_ZM1_ENN_SHIFT) )       \
                                | ( SRAM_CNTL_ZM2_ENN_MASK & (ZM2_ENN<<SRAM_CNTL_ZM2_ENN_SHIFT) )       \
                                | ( SRAM_CNTL_ZM3_ENN_MASK & (ZM3_ENN<<SRAM_CNTL_ZM3_ENN_SHIFT) )       \
                                | ( SRAM_CNTL_SRAM_SEL_MASK & (SRAM_SEL<<SRAM_CNTL_SRAM_SEL_SHIFT) )    \
                                | ( SRAM_CNTL_WR_MASK & (0b0<<SRAM_CNTL_WR_SHIFT) )                     \
                                | ( SRAM_CNTL_RD_MASK & (0b0<<SRAM_CNTL_RD_SHIFT) )

            for k in range(4095, 3500, -1):
                WDATA = 0xABCD
                RDATA = 0xFFFFFFFF
                while(RDATA!=WDATA):
                    # Set WR and RD to zero
                    CNTL_WRITE = CNTL_WRITE_DEFAULT | ( SRAM_CNTL_RD_MASK & (0b0<<SRAM_CNTL_RD_SHIFT) ) | ( SRAM_CNTL_WR_MASK & (0b0<<SRAM_CNTL_WR_SHIFT) )
                    #Zero out the CNTL reg
                    nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_CNTL_REG, data=CNTL_WRITE, console=0)
                    
                    # Form the ADDR
                    ADDR_MSB_WRITE = (k & SRAM_ADDR_MSB_DATAMASK) >> SRAM_ADDR_MSB_DATASHIFT
                    ADDR_LSB_WRITE = (k & SRAM_ADDR_LSB_DATAMASK) >> SRAM_ADDR_LSB_DATASHIFT

                    # Form the WDATA
                    WDATA_MSB_WRITE = (WDATA & SRAM_WDATA_MSB_DATAMASK) >> SRAM_WDATA_MSB_DATASHIFT
                    WDATA_LSB_WRITE = (WDATA & SRAM_WDATA_LSB_DATAMASK) >> SRAM_WDATA_LSB_DATASHIFT

                    # Write the ADDR and WDATA
                    nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_ADDR_MSB, data=ADDR_MSB_WRITE, console=0)
                    nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_ADDR_LSB, data=ADDR_LSB_WRITE, console=0)
                    nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_WDATA_MSB, data=WDATA_MSB_WRITE, console=0)
                    nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_WDATA_LSB, data=WDATA_LSB_WRITE, console=0)

                    # Set the WR flag in CNTL
                    CNTL_WRITE = CNTL_WRITE_DEFAULT | ( SRAM_CNTL_RD_MASK & (0b0<<SRAM_CNTL_RD_SHIFT) ) | ( SRAM_CNTL_WR_MASK & (0b1<<SRAM_CNTL_WR_SHIFT) )
                    nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_CNTL_REG, data=CNTL_WRITE, console=0)

                    # Clear the WR flag in CNTL
                    CNTL_WRITE = CNTL_WRITE_DEFAULT | ( SRAM_CNTL_RD_MASK & (0b0<<SRAM_CNTL_RD_SHIFT) ) | ( SRAM_CNTL_WR_MASK & (0b0<<SRAM_CNTL_WR_SHIFT) )
                    nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_CNTL_REG, data=CNTL_WRITE, console=0)

                    # Set the RD flag in CNTL
                    CNTL_WRITE = CNTL_WRITE_DEFAULT | ( SRAM_CNTL_RD_MASK & (0b1<<SRAM_CNTL_RD_SHIFT) ) | ( SRAM_CNTL_WR_MASK & (0b0<<SRAM_CNTL_WR_SHIFT) )
                    nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_CNTL_REG, data=CNTL_WRITE, console=0)

                    # Read the data from RDATA
                    nak.value = 1
                    while(nak.value != 0):
                        RDATA_MSB, nak = i2c.i2cRead(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_RDATA_MSB)

                    nak.value = 1
                    while(nak.value != 0):
                        RDATA_LSB, nak = i2c.i2cRead(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_RDATA_LSB)

                    # Format the RDATA
                    RDATA = ( (RDATA_MSB << SRAM_RDATA_MSB_DATASHIFT) & SRAM_RDATA_MSB_DATAMASK) | ( (RDATA_LSB << SRAM_RDATA_LSB_DATASHIFT) & SRAM_RDATA_LSB_DATAMASK)

                    print("SRAM: {:02b}\tADDR: {:04X}\tWDATA:{:04X}\tRDATA:{:04X}".format(SRAM_SEL, k, WDATA, RDATA))
            
            

            




    except Exception:
        i2c.closeDevice(dwf=dwfL)

    # Close the Digital Discovery Connection
    i2c.closeDevice(dwf=dwfL)



