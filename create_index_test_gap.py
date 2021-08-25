from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
from c1_vbe_test import VBEncode, VBDecode
import pprint
import sys
import re

xmldoc = open('./tipster-ap-frac/ap880212', 'r').read()
soup = BeautifulSoup('<JAPNEET>' + xmldoc + '</JAPNEET>', 'xml')
ps = PorterStemmer()
docs = soup.find_all('DOC')
docId = {}
postings = defaultdict(list)
count = 0
lastDoc = defaultdict(int)
offsets = defaultdict(int)
lenpl = defaultdict(int)
pp = pprint.PrettyPrinter()

for doc in docs:
    count += 1
    docNo = doc.find('DOCNO')
    heads = doc.find_all('HEAD')
    texts = doc.find_all('TEXT')
    if(len(heads)>0):
        id = docNo.get_text().replace(' ', '')
        docId[count] = id
        for head in heads:
            # print(head.get_text())
            # temp = re.sub(r'[^\w\s]', '', head.get_text().lower())
            # temp = temp.split()
            temp = re.split('\s|(?<!\d)[,.]|[,.](?!\d)', head.get_text().lower())
            for word in temp:
                stemmed = ps.stem(word, 0, len(word)-1)
                # print(stemmed)
                if(len(postings[stemmed])==0):
                    postings[stemmed].append(count)
                    lastDoc[stemmed]=count   
                elif(lastDoc[stemmed]!=count):
                    postings[stemmed].append(count-lastDoc[stemmed]) 
                    lastDoc[stemmed]=count       
        for text in texts:
            temp = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?\s]', text.get_text().lower())
            for word in temp:
                stemmed = ps.stem(word, 0, len(word)-1)
                # print(stemmed)
                if(len(postings[stemmed])==0):
                    postings[stemmed].append(count) 
                    lastDoc[stemmed]=count   
                elif(lastDoc[stemmed]!=count):
                    postings[stemmed].append(count-lastDoc[stemmed]) 
                    lastDoc[stemmed]=count  

byteCount = 0
cOffset = 0
destFile = open("c1_index_gap.idx", "wb")
for key in sorted(postings.keys()):
    offsets[key]=cOffset
    pl = postings[key]
    for post in pl:
        encoded = VBEncode(post)
        for j in range(0, len(encoded)):
            toWrite = encoded[j].to_bytes(1, sys.byteorder)
            cOffset+=1
            lenpl[key]+=1
            destFile.write(toWrite)
# print(offsets)

list1 = []
list2 = []
offset1 = offsets['simon']
offset2 = offsets['i']
with open("c1_index_gap.idx", "rb") as f:
        decoded = 0
        totalDecoded = 0
        f.seek(offset1)
        while(totalDecoded<lenpl['simon']):
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
        while(totalDecoded<lenpl['i']):
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
print(list1)
print(list2)
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
        print(docId[t1],i,j)
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
