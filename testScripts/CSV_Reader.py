import csv

with open('testScripts/Short_CSV.csv', 'r') as file:
    content = file.readlines()
length = len(content)


for k in range(length):
    line = content[k]
    sram_select = line[0]

    if sram_select == '0':
        SRAM_SEL = 0    
        sram_reg = int(line[2])
        wdata = int(line[4])
    
    
    elif sram_select =='1':
        SRAM_SEL = 1   
        sram_reg = int(line[2])
        wdata = int(line[4])

    elif sram_select =='2':
        SRAM_SEL = 2 
        sram_reg = int(line[2])
        wdata = int(line[4])


    elif sram_select =='3':
        SRAM_SEL = 1   
        sram_reg = int(line[2])
        wdata = int(line[4])

    else:
        pass

    print("SRAM_SEL: {:02b}\tk: {:04X}\tsram_reg:{:04X}\twdata:{:04X}".format(SRAM_SEL, k, sram_reg, wdata))


 







'''
line1 = content[0]
fig1 = line1[0]
fig2 = [1]
fig3 = [2]
print(fig1)
print(fig2)
print(fig3)
'''