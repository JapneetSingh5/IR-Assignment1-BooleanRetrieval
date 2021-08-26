from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
import sys
import json
import re
import os

f = open('c2_offsetAndLength', 'r')
offsetAndLength = json.load(f)
docId = {}
DocIdMapLength = offsetAndLength['DocIdMapLength']
indexFile = 'c2_index_gap.idx'

with open(indexFile, "rb") as f:
    jsonEncoded = f.read(DocIdMapLength)
    jsonEncoded.decode('utf-8')
    docId= json.loads(jsonEncoded)

ps = PorterStemmer()

list1 = []
list2 = []
term1 = 'panda'
term1 = ps.stem(term1.lower(), 0, len(term1)-1)
term2 = 'india'
term2= ps.stem(term2.lower(), 0, len(term2)-1)
offset1 = offsetAndLength[term1][0]
offset2 = offsetAndLength[term2][0]

with open("c2_index_gap.idx", "rb") as f:
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

with open("c2_index_gap.idx", "rb") as f:
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

f1 = open('c2_output.txt', 'w')
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
