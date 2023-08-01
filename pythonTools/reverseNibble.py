def reverseByte(x):
    x = (x & 0xF0) >> 4 | (x & 0x0F) << 4
    x = (x & 0xCC) >> 2 | (x & 0x33) << 2
    x = (x & 0xAA) >> 1 | (x & 0x55) << 1

def reverseNibble(x):
    x = (x & 0xC) >> 2 | (x & 0x3) << 2
    x = (x & 0xA) >> 1 | (x & 0x5) << 1