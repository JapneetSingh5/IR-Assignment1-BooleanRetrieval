from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
from c1_vbe_test import VBEncode, VBDecode
import sys
import json
import re
import os

f = open('c1_offsets',)
offsets = json.load(f)
f = open('c1_lenpl',)
lenpl = json.load(f)
f = open('c1_docid',)
docId = json.load(f)

list1 = []
list2 = []
term1 = 'simon'
term2 = 'i'
offset1 = offsets[term1]
offset2 = offsets[term2]
with open("c1_index_gap.idx", "rb") as f:
        decoded = 0
        totalDecoded = 0
        f.seek(offset1)
        while(totalDecoded<lenpl[term1]):
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

with open("c1_index_gap.idx", "rb") as f:
        decoded = 0
        totalDecoded = 0
        f.seek(offset2)
        while(totalDecoded<lenpl[term2]):
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
# print(list1)
# print(list2)
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
f1 = open('c1_output.txt', 'w')
while(i<len1 and j<len2):
    # print(t1, t2, file=f1)
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
