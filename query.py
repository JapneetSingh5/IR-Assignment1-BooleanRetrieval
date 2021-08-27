from bs4 import BeautifulSoup
from PorterStemmer import PorterStemmer
from collections import defaultdict
import snappy
import sys
import json
import re
import os


if __name__ == '__main__':
    queryfile = sys.argv[1]
    resultfile = sys.argv[2]
    indexfile = sys.argv[3]
    dictfile = sys.argv[4]
    c_no = -1

    f = open(dictfile, 'r')
    offsetAndLength = json.load(f)
    docId = {}
    DocIdMapOffset = offsetAndLength['DocIdMapLength'][0]
    DocIdMapLength = offsetAndLength['DocIdMapLength'][1]

    with open(indexfile, "rb") as f:
        c_no = f.read(1)
        c_no = int.from_bytes(c_no, sys.byteorder)
        # print('c', c_no)
        jsonEncoded = f.read(DocIdMapLength)
        jsonEncoded.decode('utf-8')
        docId= json.loads(jsonEncoded)

    if(c_no==-1):
        print('not_implemented')
        exit()
    
    ps = PorterStemmer()

    list1 = []
    list2 = []
    term1 = 'simon'
    term1 = ps.stem(term1.lower(), 0, len(term1)-1)
    term2 = 'i'
    term2= ps.stem(term2.lower(), 0, len(term2)-1)
    offset1 = offsetAndLength[term1][0]
    offset2 = offsetAndLength[term2][0]

    if(c_no==0):
        if term1 in offsetAndLength:
            offset1 = offsetAndLength[term1][0]
            # print(offset1)
            with open(indexfile, "rb") as f:
                    f.seek(offset1)
                    encoded = f.read(offsetAndLength[term1][1])
                    encoded = encoded.decode('utf8')
                    # print(encoded)
                    list1 = encoded.split(',')
                    list1 = [int(ele) for ele in list1]
        # print(list1)
        if term2 in offsetAndLength:
            offset2 = offsetAndLength[term2][0]
            # print(offset2)
            with open(indexfile, "rb") as f:
                    f.seek(offset2)
                    encoded = f.read(offsetAndLength[term2][1])
                    encoded = encoded.decode('utf8')
                    # print(encoded)
                    list2 = encoded.split(',')
                    list2 = [int(ele) for ele in list2]
    elif(c_no==1):
        with open(indexfile, "rb") as f:
            decoded = 0
            totalDecoded = 0
            f.seek(offset1)
            while(totalDecoded<offsetAndLength[term1][1]):
                byte = f.read(1)
                totalDecoded += 1
                if(not byte):
                    break
                readByte = int.from_bytes(byte, sys.byteorder)
                if(readByte<128):
                    decoded = decoded*128 + readByte
                    list1.append(decoded)
                    decoded = 0
                else:
                    decoded = decoded*128 + (readByte-128)
        with open(indexfile, "rb") as f:
            decoded = 0
            totalDecoded = 0
            f.seek(offset2)
            while(totalDecoded<offsetAndLength[term2][1]):
                byte = f.read(1)
                totalDecoded += 1
                if(not byte):
                    break
                readByte = int.from_bytes(byte, sys.byteorder)
                if(readByte<128):
                    decoded = decoded*128 + readByte
                    list2.append(decoded)
                    decoded = 0
                else:
                    decoded = decoded*128 + (readByte-128)
    elif(c_no==2):
        with open(indexfile, "rb") as f:
                f.seek(offset1)
                uncomp = ''
                i = 0
                while(i<offsetAndLength[term1][1]):
                    nextByte = f.read(1)
                    uncomp += '{0:08b}'.format(int.from_bytes(nextByte, sys.byteorder))
                    i+=1
                # print(uncomp)
                iter = 0
                while(iter<offsetAndLength[term1][1]*8):
                    cLen = 0
                    while(uncomp[iter]!='0'):
                        cLen+=1
                        iter+=1
                        if(iter>=offsetAndLength[term1][1]*8):
                            break
                    if(iter>=offsetAndLength[term1][1]*8 and uncomp[-1]=='1'):
                        break
                    iter+=1
                    cLen+=1
                    llx=cLen
                    lx=1
                    for _ in range(0,llx-1):
                        bit = int(uncomp[iter])
                        lx = lx*2 + bit
                        iter = iter+1
                    x = 1
                    for _ in range(lx-1):
                        bit = int(uncomp[iter])
                        x = x*2 + bit
                        iter = iter+1
                    list1.append(x)
                    # print(x)
                # print(list1)
        with open(indexfile, "rb") as f:
                f.seek(offset2)
                uncomp = ''
                i = 0
                while(i<offsetAndLength[term2][1]):
                    nextByte = f.read(1)
                    uncomp += '{0:08b}'.format(int.from_bytes(nextByte, sys.byteorder))
                    i+=1
                # print(uncomp)
                iter = 0
                while(iter<offsetAndLength[term2][1]*8):
                    cLen = 0
                    while(uncomp[iter]!='0'):
                        cLen+=1
                        iter+=1
                        if(iter>=offsetAndLength[term2][1]*8):
                            break
                    if(iter>=offsetAndLength[term2][1]*8 and uncomp[-1]=='1'):
                        break
                    iter+=1
                    cLen+=1
                    llx=cLen
                    lx=1
                    for _ in range(0,llx-1):
                        bit = int(uncomp[iter])
                        lx = lx*2 + bit
                        iter = iter+1
                    x = 1
                    for _ in range(lx-1):
                        bit = int(uncomp[iter])
                        x = x*2 + bit
                        iter = iter+1
                    list2.append(x)
                    # print(x)
                # print(list2)       
    elif(c_no==3):
        with open(indexfile, "rb") as f:
                f.seek(offset1)
                comp = f.read(offsetAndLength[term1][1])
                # print(comp)
                uncomp = snappy.uncompress(comp)
                strList1 = uncomp.decode('utf8')
                strList1 = strList1.split(' ')
                # print(strList1)
                list1 = [int(ele) for ele in strList1[0:-1]]
        with open(indexfile, "rb") as f:
                f.seek(offset2)
                comp = f.read(offsetAndLength[term2][1])
                # print(comp)
                uncomp = snappy.decompress(comp)
                strList2 = uncomp.decode('utf8')
                strList2 = strList2.split(' ')
                # print(strList2)
                list2 = [int(ele) for ele in strList2[0:-1]]
    # print(list1)
    # print(list2)
    elif(c_no==4):
        print('not implemented')
        exit()
    elif(c_no==5):
        print('not implemented')
        exit()
    else: 
        print('not_implemented')
        exit()
    
    f1 = open(resultfile, 'w')
    len1 = len(list1)
    len2 = len(list2)
    i = 0
    j = 0
    t1 = 0
    t2 = 0
    if(len1>0):
        t1=list1[0]
    if(len2>0):
        t2=list2[0]
    while(i<len1 and j<len2):
        # print(t1, t2)
        if(t1==t2):
            print(docId[str(t1)], file=f1)
            i+=1
            j+=1
            if(i<len1):
                t1+=list1[i]
            if(j<len2):
                t2+=list2[j]
        elif(t1<t2):
            i+=1
            if(i<len1):
                t1+=list1[i]       
        else: 
            j+=1
            if(j<len2):
                t2+=list2[j]       