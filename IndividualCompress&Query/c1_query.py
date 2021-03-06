from bs4 import BeautifulSoup
from PorterStemmer import PorterStemmer
from collections import defaultdict
import sys
import json
import re
import os

f = open('c1_offsetAndLength', 'r')
offsetAndLength = json.load(f)
docId = {}
DocIdMapLength = offsetAndLength['DocIdMapLength']
indexFile = 'c1_index_gap.idx'

with open(indexFile, "rb") as f:
    jsonEncoded = f.read(DocIdMapLength)
    jsonEncoded.decode('utf-8')
    docId= json.loads(jsonEncoded)

ps = PorterStemmer()

list1 = []
list2 = []
term1 = 'simon'
term1 = ps.stem(term1.lower(), 0, len(term1)-1)
term2 = 'i'
term2= ps.stem(term2.lower(), 0, len(term2)-1)
# print(term1, term2)
offset1 = offsetAndLength[term1][0]
offset2 = offsetAndLength[term2][0]
with open(indexFile, "rb") as f:
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

with open(indexFile, "rb") as f:
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
