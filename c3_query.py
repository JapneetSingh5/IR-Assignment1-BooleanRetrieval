from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
from c1_vbe_test import VBEncode, VBDecode
import snappy
import sys
import json
import re
import os

f = open('c3_offsets',)
offsets = json.load(f)
f = open('c3_lenpl',)
lenpl = json.load(f)
f = open('c3_docid',)
docId = json.load(f)

list1 = []
list2 = []
offset1 = offsets['simon']
offset2 = offsets['i']
with open("c3_index_gap.idx", "rb") as f:
        f.seek(offset1)
        comp = f.read(lenpl['simon'])
        # print(comp)
        uncomp = snappy.uncompress(comp)
        strList1 = uncomp.decode('utf8')
        strList1 = strList1.split(' ')
        # print(strList1)
        list1 = [int(ele) for ele in strList1[0:-1]]

with open("c3_index_gap.idx", "rb") as f:
        f.seek(offset2)
        comp = f.read(lenpl['i'])
        # print(comp)
        uncomp = snappy.decompress(comp)
        strList2 = uncomp.decode('utf8')
        strList2 = strList2.split(' ')
        # print(strList2)
        list2 = [int(ele) for ele in strList2[0:-1]]
# print(list1)
# print(list2)
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
