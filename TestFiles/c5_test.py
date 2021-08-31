import math 
import sys

def c1_encode(n):
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

pl1 = [2, 5, 4, 16, 8, 10, 52, 6, 7, 10, 14, 3, 3, 7, 2, 2, 4, 1, 7, 3]
pl2 = [8, 11, 12, 19, 24, 34, 42, 62, 214, 422]
pl3 = [10]
pl4 = [10, 11, 12]
pl5 = [2, 34, 28, 19, 11, 4, 2, 1, 3, 14, 11, 2, 2, 11, 6, 9, 9, 3]

def c5_encode(pl):
    b = pl[0]
    maxEle = pl[0]
    k = 2
    cutOff = 0
    if(len(pl)==1):
        comp1 = ['{0:08b}'.format(x) for x in c1_encode(b)]
        comp2 = ['{0:08b}'.format(x) for x in c1_encode(k)]
        return(''.join(comp1)+''.join(comp2)+'11'*(cutOff+1))
        # print(b,k,['{0:08b}'.format(x) for x in c1_encode(b)])
    while(cutOff<len(pl) and (cutOff+1)*100/len(pl)<80):
        b = min(b, pl[cutOff])
        # k = max(math.floor(math.log2(pl[cutOff]-b)) + 1, k)
        maxEle = max(maxEle, pl[cutOff])
        # print(cutOff)
        cutOff += 1
    if(len(pl)>1):
        k = math.floor(math.log2(maxEle-b+2)) + 1
    while(cutOff<len(pl) and pl[cutOff]<=maxEle and pl[cutOff]>=b):
        # print(pl[cutOff], pl[cutOff]-b, math.floor(math.log2(pl[cutOff]-b)) + 1, k)
        cutOff+=1
    print(b)   
    print(k)
    format_k = '{0:0'+str(k)+'b}'
    comp1 = ''.join(['{0:08b}'.format(x) for x in c1_encode(b)])
    comp2 = ''.join(['{0:08b}'.format(x) for x in c1_encode(k)])
    comp3 = ''.join([format_k.format(x-b) for x in pl[0:cutOff]])
    print('here', cutOff)
    if(cutOff==len(pl)):
        # print(b,k,['{0:08b}'.format(x) for x in c1_encode(b)], ['{0:08b}'.format(x) for x in c1_encode(cutOff+1)], ['{0:06b}'.format(x-b) for x in pl[1:cutOff]])
        to_write = comp1+comp2+comp3
        padding = (8 - (len(to_write)%8))%8
        return to_write+('1'*padding)
    else: 
        print('here')
        # print(b,k,['{0:08b}'.format(x) for x in c1_encode(b)], ['{0:08b}'.format(x) for x in c1_encode(cutOff+1)], ['{0:06b}'.format(x-b) for x in pl[1:cutOff]], pl[cutOff:])
        # print(pl[cutOff:])
        comp4 = [['{0:08b}'.format(x) for x in c1_encode(ele)] for ele in pl[cutOff:]]
        # print(comp4)
        comp4 = ''.join([''.join(x) for x in comp4])
        # print(comp4)
        to_write = comp1+comp2+comp3+('1'*k)+comp4
        padding = (8 - (len(to_write)%8))%8
        return to_write+('1'*padding)
    # comp1 = ['{0:08b}'.format(x) for x in c1_encode(b)]
    # comp2 = ['{0:08b}'.format(x) for x in c1_encode(k)]
    # comp3 = ['{0:06b}'.format(x-b) for x in pl[1:cutOff]]
    # return(''.join(comp1)+''.join(comp2)+''.join(comp3))


def c5_decode(x):
    pl=[]
    i = 0
    b = 0
    k = 0
    while(True):
        byte = x[i:i+8]
        # print(byte)
        readByte = int(byte, 2)
        # print(readByte)
        i+=8
        if(readByte<128):
            b = b*128 + readByte
            break
        else:
            b = b*128 + (readByte-128)
    # print(b)
    while(True):
        byte = x[i:i+8]
        # print(byte)
        readByte = int(byte, 2)
        # print(readByte)
        i+=8
        if(readByte<128):
            k = k*128 + readByte
            break
        else:
            k = k*128 + (readByte-128)
    # print(k)
    pl.append(b)
    if(k==2):
        return pl
    while(i<len(x)):
        block = x[i:i+k]
        # print(block)
        i+=k
        block_val = int(block, 2)
        if(block_val == (2**k - 1)):
            break
        else: 
            pl.append(b+block_val)
    excess_element = 0
    while(i+8<=len(x)):
        byte = x[i:i+8]
        # print(byte)
        readByte = int(byte, 2)
        # print(readByte)
        i+=8
        if(readByte<128):
            excess_element = excess_element*128 + readByte
            pl.append(excess_element)
            excess_element = 0
        else:
            excess_element = excess_element*128 + (readByte-128)
    return pl








print(pl1)
print(c5_encode(pl1))
print(c5_decode(c5_encode(pl1)))

print(pl2)
print(c5_decode(c5_encode(pl2)))
print(c5_encode(pl2))

print(pl3)
print(c5_decode(c5_encode(pl3)))
print(c5_encode(pl3))

print(pl4)
print(c5_decode(c5_encode(pl4)))
print(c5_encode(pl4))
    

# for i in pl1:
#     print(i.to_bytes(1, sys.byteorder))
# print(bytearray(pl1))

