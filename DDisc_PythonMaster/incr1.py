import re
import time

file = open('shortReg.txt', 'r')

read = file.readlines()
global inc
inc = 1
length = len(read)
while (inc<length):

    print('-----------------------------------------------------------------------')
    
    line = read[inc-1]
    val1 = line[0]
    
    if val1 == '1':

        regR = read[inc]
        regNum = int(regR[0])
        
        inc = inc+2

        reginc = 0
        while (reginc < regNum):
            inc = inc+1
            reginc = reginc+1

            reg1 = read[inc-2]

            hexreg = re.findall(r'[0-9A-Fa-f]+', reg1)
            sREG = hexreg[0]
            sData = hexreg[1]
            iREG = int(sREG, 16)
            iData = int(sData, 16)
            REG = hex(iREG)
            Data = hex(iData)
            # Print the extracted values
            print("Register:", REG)
            print("Data:    ", Data)
        
        time.sleep(1e-6)
        inc = inc+2
    
    
    else:
        print("Error in text")  
    


        
        

    
