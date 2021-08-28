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

def create_lists_to_intersect(c_no, query, indexfile):
    # print(query)
    lists_to_intersect = []
    for term in query:
        # print(term)
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
                # print(uncomp)
                iter = 0
                while(iter<offsetAndLength[term][1]*8):
                    cLen = 0
                    while(uncomp[iter]!='0'):
                        cLen+=1
                        iter+=1
                        if(iter>=offsetAndLength[term][1]*8):
                            break
                    if(iter>=offsetAndLength[term][1]*8 and uncomp[-1]=='1'):
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
                    term_list.append(x)     
                lists_to_intersect.append(term_list)
        elif(c_no==3):
            offset = offsetAndLength[term][0]
            with open(indexfile, "rb") as f:
                f.seek(offset)
                comp = f.read(offsetAndLength[term][1])
                uncomp = snappy.uncompress(comp)
                strList1 = uncomp.decode('utf8')
                strList1 = strList1.split(' ')
                term_list = [int(ele) for ele in strList1[0:-1]]
                lists_to_intersect.append(term_list)
        elif(c_no==4 or c_no==5 or c_no>5 or c_no<0):
            print('not implemented')
            exit()
    return sorted(lists_to_intersect, key=len)



if __name__ == '__main__':
    start = time.time()
    queryfile = sys.argv[1]
    resultfile = sys.argv[2]
    indexfile = sys.argv[3]
    dictfile = sys.argv[4]
    c_no = -1

    exclist = ',.:;"’(){}[]\n`\''
    table = str.maketrans(exclist, ' '*len(exclist), '')

    f = open(dictfile, 'r')
    offsetAndLength = json.load(f)
    docId = {}
    DocIdMapOffset = offsetAndLength['DocIdMapLength'][0]
    DocIdMapLength = offsetAndLength['DocIdMapLength'][1]
    # SWOffset = offsetAndLength['Stopwords'][0]
    # SWLength = offsetAndLength['Stopwords'][1]
    f.close()

    stopwords = set()
    with open(indexfile, "rb") as f:
        c_no = f.read(1)
        c_no = int.from_bytes(c_no, sys.byteorder)
        # print('c', c_no)
        jsonEncoded = f.read(DocIdMapLength)
        jsonEncoded.decode('utf-8')
        docId= json.loads(jsonEncoded)
        # if(SWLength>0):
        #     sw_str = f.read(SWLength).decode()
        #     stopwords = set(list(sw_str))


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
    print(queries)
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
        total = 0
        for doc in result: 
            total+=doc
            print('Q'+str(qCounter), docId[str(total)], '1.0', file=f1)
        qCounter+=1  
        f1.close()  
    end = time.time()
    print(end-start)