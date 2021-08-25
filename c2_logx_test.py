import sys
from struct import pack, unpack

def C2Encode(x):
    encoded = ""
    lx = x.bit_length()
    llx = lx.bit_length()
    for _ in range(0, llx-1):
        encoded += '1'
    encoded += '0'
    a1 = lx
    b1 = llx-1
    temp1 = ""
    for _ in range(0,b1):
        temp1 = str(a1%2) + temp1
        a1 = a1//2
    a2 = x
    b2 = lx-1
    temp2 = ""
    for _ in range(0,b2):
        temp2 = str(a2%2) + temp2
        a2 = a2//2
    encoded += temp1
    encoded += temp2
    return encoded

def C2Decode(encoded):
    i = 0
    while(encoded[i]!='0'):
        i=i+1
    i = i + 1
    llx = i
    lx = 1
    for _ in range(0,llx-1):
        bit = int(encoded[i])
        lx = lx*2 + bit
        i = i+1
    x = 1
    for _ in range(lx-1):
        bit = int(encoded[i])
        x = x*2 + bit
        i = i+1
    return x

# https://gist.github.com/jogonba2/0a813e1b6a4d437a6dfe

# encoded = C2Encode(13)
# decoded = C2Decode(encoded)
# print(str(encoded) + " " + str(decoded))

destFile = open("c2_index_test.idx", "wb")
for i in range(1, 1000):
    encoded = int(C2Encode(i))
    toWrite = encoded.to_bytes((encoded.bit_length()+7)//8, sys.byteorder)
    destFile.write(toWrite)
destFile.close()


with open("c2_index_test.idx", "rb") as f:
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

txtFile =  open("c2_index_test.txt", "w")
for i in range(0, 1000):
    txtFile.write(str(i))
        



