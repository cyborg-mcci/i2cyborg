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

    inc +=1
    
    if val1 == '1':   # WRITE SEQUENCE

        regR = read[inc-1]
        regNum = int(regR[0])
        
        inc +=1

        reginc = 0
        while (reginc < regNum):
            
            reginc = reginc+1

            reg1 = read[inc-1]
            inc +=1

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

        
            
        
        #time.sleep(1e-6)
        #inc = inc+2
    
    elif val1 == '2':   # READ SEQUENCE

        regR = read[inc-1]
        regNum = int(regR[0])
        
        inc +=1

        reginc = 0

        while (reginc < regNum):
            
            reginc = reginc+1

            reg1 = read[inc-1]
            inc +=1

            hexreg = re.findall(r'[0-9A-Fa-f]+', reg1)
            sREG = hexreg[0]
            iREG = int(sREG, 16)
            REG = hex(iREG)
            print("Register:", REG)
        

    
    elif val1 == '3':   # WAIT SEQUENCE
        
        wait_line = read[inc-1]
        wait_timeS = re.findall(r'\d+', wait_line)
        wait_time = int(wait_timeS[0])

        
        time.sleep(wait_time*1e-6)
        inc = inc+1
    
    
    else:
        print("Error in text")  
    


        
        

    
