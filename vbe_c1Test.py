import sys
from struct import pack, unpack

def VBEncode(n):
    bytes = [] 
    bytes.append(n%128)
    n = n//128
    while(True):
        if(n==0):           
            break
        else: 
            bytes.insert(0, n%128 + 128)
            n = n//128
    return bytes

def VBDecode(bytes):
    n = 0
    for i in range(0, len(bytes)-1):
        n = (n*128 + (bytes[i]-128))
    n = n*128 + bytes[len(bytes)-1]
    return n

destFile = open("indexTest.idx", "wb")
for i in range(1, 1000):
    encoded = VBEncode(i)
    for j in range(0, len(encoded)):
        toWrite = encoded[j].to_bytes(1, sys.byteorder)
        destFile.write(toWrite)
destFile.close()


with open("indexTest.idx", "rb") as f:
        decoded = 0
        while(True):
            byte = f.read(1)
            if(not byte):
                break
            readByte = int.from_bytes(byte, sys.byteorder)
            if(readByte<128):
                decoded = decoded*128 + readByte
                print(decoded)
                decoded = 0
            else:
                decoded = decoded*128 + (readByte-128)
        



