from bs4 import BeautifulSoup
from PorterStemmer import PorterStemmer
from collections import defaultdict
import snappy
import sys
import json
import re
import os
import string
import time

def c5_decode(x):
    pl=[]
    i = 0
    b = 0
    k = 0
    while(True):
        byte = x[i:i+8]
        readByte = int(byte, 2)
        i+=8
        if(readByte<128):
            b = b*128 + readByte
            break
        else:
            b = b*128 + (readByte-128)
    while(True):
        byte = x[i:i+8]
        readByte = int(byte, 2)
        i+=8
        if(readByte<128):
            k = k*128 + readByte
            break
        else:
            k = k*128 + (readByte-128)
    if(k==2):
        return pl
    while(i<len(x)):
        block = x[i:i+k]
        i+=k
        block_val = int(block, 2)
        if(block_val == (2**k - 1)):
            break
        else: 
            pl.append(b+block_val)
    excess_element = 0
    while(i+8<=len(x)):
        byte = x[i:i+8]
        readByte = int(byte, 2)
        i+=8
        if(readByte<128):
            excess_element = excess_element*128 + readByte
            pl.append(excess_element)
            excess_element = 0
        else:
            excess_element = excess_element*128 + (readByte-128)
    return pl

def create_lists_to_intersect(c_no, query, indexfile):
    lists_to_intersect = []
    for term in query:
        term_list = []
        if term not in offsetAndLength:
            term_list=[]
            lists_to_intersect.append(term_list)
        elif(c_no==0):
            offset = offsetAndLength[term][0]
            with open(indexfile, "rb") as f:
                f.seek(offset)
                encoded = f.read(offsetAndLength[term][1])
                encoded = encoded.decode('utf8')
                term_list = encoded.split(',')
                term_list = [int(ele) for ele in term_list]
            lists_to_intersect.append(term_list)
        elif(c_no==1):
            offset = offsetAndLength[term][0]
            with open(indexfile, "rb") as f:
                decoded = 0
                totalDecoded = 0
                f.seek(offset)
                while(totalDecoded<offsetAndLength[term][1]):
                    byte = f.read(1)
                    totalDecoded += 1
                    if(not byte):
                        break
                    readByte = int.from_bytes(byte, sys.byteorder)
                    if(readByte<128):
                        decoded = decoded*128 + readByte
                        term_list.append(decoded)
                        decoded = 0
                    else:
                        decoded = decoded*128 + (readByte-128)
            lists_to_intersect.append(term_list)
        elif(c_no==2):
            offset = offsetAndLength[term][0]
            with open(indexfile, "rb") as f:
                f.seek(offset)
                uncomp = ''
                i = 0
                while(i<offsetAndLength[term][1]):
                    nextByte = f.read(1)
                    uncomp += '{0:08b}'.format(int.from_bytes(nextByte, sys.byteorder))
                    i+=1
                j = 0
                while(j<offsetAndLength[term][1]*8):
                    c_len = 0
                    while(uncomp[j]!='0'):
                        c_len+=1
                        j+=1
                        if(j>=offsetAndLength[term][1]*8):
                            break
                    if(j>=offsetAndLength[term][1]*8 and uncomp[-1]=='1'):
                        break
                    j+=1
                    c_len+=1
                    llx=c_len
                    lx=1
                    for _ in range(0,llx-1):
                        bit = int(uncomp[j])
                        lx = lx*2 + bit
                        j = j+1
                    x = 1
                    for _ in range(lx-1):
                        bit = int(uncomp[j])
                        x = x*2 + bit
                        j = j+1
                    term_list.append(x)     
                lists_to_intersect.append(term_list)
        elif(c_no==3):
            offset = offsetAndLength[term][0]
            with open(indexfile, "rb") as f:
                f.seek(offset)
                comp = f.read(offsetAndLength[term][1])
                uncomp = snappy.uncompress(comp)
                strList1 = uncomp.decode()
                strList1 = strList1.split(',')
                term_list = [int(ele) for ele in strList1]
                lists_to_intersect.append(term_list)
        elif(c_no==4 or c_no>5 or c_no<0):
            print('not implemented')
            exit()
        elif(c_no==5):
            offset = offsetAndLength[term][0]
            with open(indexfile, "rb") as f:
                f.seek(offset)
                comp = list(f.read(offsetAndLength[term][1]))
                comp = ''.join(['{0:08b}'.format(x) for x in comp])
                uncomp = c5_decode(comp)
                lists_to_intersect.append(uncomp)
    return sorted(lists_to_intersect, key=len)



if __name__ == '__main__':
    start = time.time()
    queryfile = sys.argv[1]
    resultfile = sys.argv[2]
    indexfile = sys.argv[3]
    dictfile = sys.argv[4]
    c_no = -1

    exclist = ',.:;"(){}[]\n`\''
    table = str.maketrans(exclist, ' '*len(exclist), '')

    f = open(dictfile, 'r')
    offsetAndLength = json.load(f)
    docId = {}
    docId = offsetAndLength['DocIdMapLength']
    f.close()

    stopwords = set()
    with open(indexfile, "rb") as f:
        c_no = f.read(1)
        c_no = int.from_bytes(c_no, sys.byteorder)


    if(c_no==-1):
        print('not_implemented')
        exit()
    
    ps = PorterStemmer()

    queries = []
    with open(queryfile, 'r') as f:
        for line in f:
            temp = line.rstrip()
            tempList = temp = temp.translate(str.maketrans(table)).split()
            if(len(tempList)>0):
                queries.append(tempList)
    for query in queries:
        for i in range(0, len(query)):
            query[i] = ps.stem(query[i].lower(), 0, len(query[i])-1)
    qCounter = 0
    # print(queries)
    with open(resultfile,'w') as f:
        f.truncate(0)
    for query in queries:
        lists_to_intersect = create_lists_to_intersect(c_no, query, indexfile)        
        f1 = open(resultfile, 'a')    
        result = []
        if(len(lists_to_intersect)>0):
            result = lists_to_intersect[0]
        else: 
            result = []
            continue 
        for list_no in range(1, len(lists_to_intersect)): 
            newResult=[]   
            len1 = len(result)
            len2 = len(lists_to_intersect[list_no])
            i = 0
            j = 0
            t1 = 0
            t2 = 0
            lastEle = 0
            if(len1>0):
                t1=result[0]
            else:
                result=[]
                break
            if(len2>0):
                t2=lists_to_intersect[list_no][0]
            else: 
                result=[]
                break
            while(i<len1 and j<len2):
                # print(t1, t2)
                if(t1==t2):
                    # print(t1, lastEle, t2)
                    newResult.append(t1-lastEle)
                    lastEle = t1
                    i+=1
                    j+=1
                    if(i<len1):
                        t1+=result[i]
                    if(j<len2):
                        t2+=lists_to_intersect[list_no][j]
                elif(t1<t2):
                    i+=1
                    if(i<len1):
                        t1+=result[i]       
                else: 
                    j+=1
                    if(j<len2):
                        t2+=lists_to_intersect[list_no][j] 
            result = newResult 
            # print(result)
        total = 0

        for doc in result: 
            total+=doc
            print('Q'+str(qCounter)+' '+docId[str(total)]+' 1.0 ', file=f1)
        qCounter+=1  
        f1.close()  
    end = time.time()
    print(end-start)