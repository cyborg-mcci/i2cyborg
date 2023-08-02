import i2Constants as i2c
import DDDfunctions as ddf
import dwfconstants as dwfc
import time

if __name__ == "__main__":
    


    try: 
        # Load the DWF library
        dwfL = ddf.loadDwf()

        # Open the Digital Discovery connection
        dwfH = ddf.openDevice(dwfL)

        # Configure the I2C connection
        nak = ddf.i2cConfig(dwf=dwfL, hdwf=dwfH, RateSet=i2c.i2cRate, SCL=i2c.i2cSCL, SDA=i2c.i2cSDA)

        # First prompt the user to hit RSTB (Automate this using GPIO later)
        input("Press the RSTB button. Hit ENTER when complete")

        # Prompt the user to lock at Fmin
        input("Lock the CLK_RS at the minimum frequency. Hit ENTER when complete")


        
        # Set CLK_RS divider to max value
        nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cCLKRSReg, data=0x0F)
        # Disable the CCRO
        nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cPWRCNTLReg, data=0x00)
        # Disable the aux output pins
        nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cDEBUGReg, data=0b00011000)


        # SRAM Fill Section
        SRAM_SEL_LIST = [0b00, 0b01, 0b10, 0b11]
        for SRAM_SEL in SRAM_SEL_LIST:
            for k in range(4095, 0, -1):
                WDATA = 0x0001
                RDATA = 0xFFFFFFFF
                while(RDATA!=WDATA):

                    ZM0_ENN = 0
                    ZM1_ENN = 0
                    ZM2_ENN = 0
                    ZM3_ENN = 0
                    # Setting the initial SRAM_CNTL write for the loop
                    CNTL_WRITE_DEFAULT =  ( i2c.SRAM_CNTL_ZM0_ENN_MASK & (ZM0_ENN<<i2c.SRAM_CNTL_ZM0_ENN_SHIFT) )         \
                                        | ( i2c.SRAM_CNTL_ZM1_ENN_MASK & (ZM1_ENN<<i2c.SRAM_CNTL_ZM1_ENN_SHIFT) )       \
                                        | ( i2c.SRAM_CNTL_ZM2_ENN_MASK & (ZM2_ENN<<i2c.SRAM_CNTL_ZM2_ENN_SHIFT) )       \
                                        | ( i2c.SRAM_CNTL_ZM3_ENN_MASK & (ZM3_ENN<<i2c.SRAM_CNTL_ZM3_ENN_SHIFT) )       \
                                        | ( i2c.SRAM_CNTL_SRAM_SEL_MASK & (SRAM_SEL<<i2c.SRAM_CNTL_SRAM_SEL_SHIFT) )    \
                                        | ( i2c.SRAM_CNTL_WR_MASK & (0b0<<i2c.SRAM_CNTL_WR_SHIFT) )                     \
                                        | ( i2c.SRAM_CNTL_RD_MASK & (0b0<<i2c.SRAM_CNTL_RD_SHIFT) )


                    # Ensure the CLK divider is still at the correct value for speed
                    nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cCLKRSReg, data=0x0F, console=0)
                    # Set WR and RD to zero
                    #CNTL_WRITE = CNTL_WRITE_DEFAULT | ( SRAM_CNTL_RD_MASK & (0b0<<SRAM_CNTL_RD_SHIFT) ) | ( SRAM_CNTL_WR_MASK & (0b0<<SRAM_CNTL_WR_SHIFT) )
                    #nak = i2c.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2cAddress, reg=SRAM_CNTL_REG, data=CNTL_WRITE, console=0)
                    
                    # Form the ADDR
                    ADDR_MSB_WRITE = (k & i2c.SRAM_ADDR_MSB_DATAMASK) >> i2c.SRAM_ADDR_MSB_DATASHIFT
                    ADDR_LSB_WRITE = (k & i2c.SRAM_ADDR_LSB_DATAMASK) >> i2c.SRAM_ADDR_LSB_DATASHIFT

                    # Form the WDATA
                    WDATA_MSB_WRITE = (WDATA & i2c.SRAM_WDATA_MSB_DATAMASK) >> i2c.SRAM_WDATA_MSB_DATASHIFT
                    WDATA_LSB_WRITE = (WDATA & i2c.SRAM_WDATA_LSB_DATAMASK) >> i2c.SRAM_WDATA_LSB_DATASHIFT

                    # Write the ADDR and WDATA
                    nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.SRAM_ADDR_MSB, data=ADDR_MSB_WRITE, console=0)
                    nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.SRAM_ADDR_LSB, data=ADDR_LSB_WRITE, console=0)
                    nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.SRAM_WDATA_MSB, data=WDATA_MSB_WRITE, console=0)
                    nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.SRAM_WDATA_LSB, data=WDATA_LSB_WRITE, console=0)

                    # Set the WR flag in CNTL
                    CNTL_WRITE = CNTL_WRITE_DEFAULT | ( i2c.SRAM_CNTL_RD_MASK & (0b0<<i2c.SRAM_CNTL_RD_SHIFT) ) | ( i2c.SRAM_CNTL_WR_MASK & (0b1<<i2c.SRAM_CNTL_WR_SHIFT) )
                    nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.SRAM_CNTL_REG, data=CNTL_WRITE, console=0)

                    # Clear the WR flag in CNTL
                    #CNTL_WRITE = CNTL_WRITE_DEFAULT | ( SRAM_CNTL_RD_MASK & (0b0<<SRAM_CNTL_RD_SHIFT) ) | ( SRAM_CNTL_WR_MASK & (0b0<<SRAM_CNTL_WR_SHIFT) )
                    #nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.SRAM_CNTL_REG, data=i2c.CNTL_WRITE, console=0)

                    # Set the RD flag in CNTL
                    CNTL_WRITE = CNTL_WRITE_DEFAULT | ( i2c.SRAM_CNTL_RD_MASK & (0b1<<i2c.SRAM_CNTL_RD_SHIFT) ) | ( i2c.SRAM_CNTL_WR_MASK & (0b0<<i2c.SRAM_CNTL_WR_SHIFT) )
                    nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.SRAM_CNTL_REG, data=CNTL_WRITE, console=0)


                    # Read the data from RDATA
                    nak.value = 1
                    while(nak.value != 0):
                        RDATA_MSB, nak = ddf.i2cRead(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.SRAM_RDATA_MSB)

                    nak.value = 1
                    while(nak.value != 0):
                        RDATA_LSB, nak = ddf.i2cRead(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.SRAM_RDATA_LSB)


                    # Format the RDATA
                    RDATA = ( (RDATA_MSB << i2c.SRAM_RDATA_MSB_DATASHIFT) & i2c.SRAM_RDATA_MSB_DATAMASK) | ( (RDATA_LSB << i2c.SRAM_RDATA_LSB_DATASHIFT) & i2c.SRAM_RDATA_LSB_DATAMASK)

                    print("SRAM: {:02b}\tADDR: {:04X}\tWDATA:{:04X}\tRDATA:{:04X}".format(SRAM_SEL, k, WDATA, RDATA))

            
            

            

        # Ensure the other important regs are still good
        for k in range(1,100):
            nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cCLKRSReg, data=0x0F, console=0)
            nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cLSBCORRReg, data=0x16, console=0)
            nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cDEBUGReg, data=0x18, console=0)
            nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cPWRCNTLReg, data=0x02, console=0)
            nak = ddf.i2cWriteConfirm(dwf=dwfL, hdwf=dwfH, nak=nak, addr=i2c.i2cAddress, reg=i2c.i2cAFECNTLReg, data=0x0B, console=0)




    except Exception:
        ddf.closeDevice(dwf=dwfL)


    # Close the Digital Discovery Connection
    ddf.closeDevice(dwf=dwfL)



