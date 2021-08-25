from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
from c1_vbe_test import VBEncode, VBDecode
import sys
import json
import re
import os

f = open('c2_offsets',)
offsets = json.load(f)
f = open('c2_lenpl',)
lenpl = json.load(f)
f = open('c2_docid',)
docId = json.load(f)

list1 = []
list2 = []
term1 = 'simon'
term2 = 'i'
offset1 = offsets[term1]
offset2 = offsets[term2]
with open("c2_index_gap.idx", "rb") as f:
        f.seek(offset1)
        uncomp = ''
        i = 0
        while(i<lenpl[term1]):
            nextByte = f.read(1)
            uncomp += '{0:08b}'.format(int.from_bytes(nextByte, sys.byteorder))
            i+=1
        # print(uncomp)
        iter = 0
        while(iter<lenpl[term1]*8):
            cLen = 0
            while(uncomp[iter]!='0'):
                cLen+=1
                iter+=1
                if(iter>=lenpl[term1]*8):
                    break
            if(iter>=lenpl[term1]*8 and uncomp[-1]=='1'):
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
        while(i<lenpl[term2]):
            nextByte = f.read(1)
            uncomp += '{0:08b}'.format(int.from_bytes(nextByte, sys.byteorder))
            i+=1
        # print(uncomp)
        iter = 0
        while(iter<lenpl[term2]*8):
            cLen = 0
            while(uncomp[iter]!='0'):
                cLen+=1
                iter+=1
                if(iter>=lenpl[term2]*8):
                    break
            if(iter>=lenpl[term2]*8 and uncomp[-1]=='1'):
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
