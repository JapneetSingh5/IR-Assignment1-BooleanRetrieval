from bs4 import BeautifulSoup
from PorterStemmer import PorterStemmer
from collections import defaultdict
import snappy
import sys
import json
import re
import os

f = open('c3_offsetAndLength', 'r')
offsetAndLength = json.load(f)
docId = {}
DocIdMapLength = offsetAndLength['DocIdMapLength']
indexFile = 'c3_index_gap.idx'

with open(indexFile, "rb") as f:
    jsonEncoded = f.read(DocIdMapLength)
    jsonEncoded.decode('utf-8')
    docId= json.loads(jsonEncoded)

ps = PorterStemmer()

list1 = []
list2 = []
term1 = 'waterfall'
term1 = ps.stem(term1.lower(), 0, len(term1)-1)
term2 = 'open'
term2= ps.stem(term2.lower(), 0, len(term2)-1)
offset1 = offsetAndLength[term1][0]
offset2 = offsetAndLength[term2][0]

with open(indexFile, "rb") as f:
        f.seek(offset1)
        comp = f.read(offsetAndLength[term1][1])
        # print(comp)
        uncomp = snappy.uncompress(comp)
        strList1 = uncomp.decode('utf8')
        strList1 = strList1.split(' ')
        # print(strList1)
        list1 = [int(ele) for ele in strList1[0:-1]]

with open(indexFile, "rb") as f:
        f.seek(offset2)
        comp = f.read(offsetAndLength[term2][1])
        # print(comp)
        uncomp = snappy.decompress(comp)
        strList2 = uncomp.decode('utf8')
        strList2 = strList2.split(' ')
        # print(strList2)
        list2 = [int(ele) for ele in strList2[0:-1]]
print(list1)
print(list2)
f1 = open('c3_output.txt', 'w')
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
