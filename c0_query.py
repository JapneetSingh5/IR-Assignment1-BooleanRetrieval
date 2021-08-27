from bs4 import BeautifulSoup
from PorterStemmer import PorterStemmer
from collections import defaultdict
import sys
import json
import re
import os

f = open('c0_offsetAndLength', 'r')
offsetAndLength = json.load(f)
docId = {}
DocIdMapLength = offsetAndLength['DocIdMapLength']
indexFile = 'c0_index_gap.idx'

with open(indexFile, "rb") as f:
    jsonEncoded = f.read(DocIdMapLength)
    jsonEncoded.decode('utf-8')
    docId= json.loads(jsonEncoded)

ps = PorterStemmer()

list1 = []
list2 = []
term1 = 'i'
term1 = ps.stem(term1.lower(), 0, len(term1)-1)
term2 = 'simon'
term2= ps.stem(term2.lower(), 0, len(term2)-1)
if term1 in offsetAndLength:
    offset1 = offsetAndLength[term1][0]
    # print(offset1)
    with open(indexFile, "rb") as f:
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
    with open(indexFile, "rb") as f:
            f.seek(offset2)
            encoded = f.read(offsetAndLength[term2][1])
            encoded = encoded.decode('utf8')
            # print(encoded)
            list2 = encoded.split(',')
            list2 = [int(ele) for ele in list2]
# print(list2)
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
f1 = open('c0_output.txt', 'w')
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
