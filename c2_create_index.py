from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
from c2_logx_test import C2Encode, C2Decode
import sys
import re
import os
import json


ps = PorterStemmer()
def def_value():
    return "Not Present"
docId = defaultdict(def_value)
postings = defaultdict(list)
count = 0
lastDoc = defaultdict(int)
offsets = defaultdict(int)
lenpl = defaultdict(int)
iter = 0
filecount = 0
doclist = sorted(os.listdir('tipster-ap-frac'))
total = len(doclist)
for file in doclist:
    filecount += 1
    f = os.path.join('tipster-ap-frac', file)
    if(file=='ap890520'): 
        continue
    # iter+=1
    # if(iter>10):
    #     break
    xmldoc = open(f, 'r').read()
    soup = BeautifulSoup('<JAPNEET>' + xmldoc + '</JAPNEET>', 'xml')
    docs = soup.find_all('DOC')
    print('Processing ', f, '( ', filecount, ' out of ', total, ' processed )')
    for doc in docs:
        count += 1
        docNo = doc.find('DOCNO')
        heads = doc.find_all('HEAD')
        texts = doc.find_all('TEXT')
        id = docNo.get_text().replace(' ', '')
        docId[count] = id
        if(len(heads)>0):
            for head in heads:
                temp = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?\s]', head.get_text())
                for word in temp:
                    stemmed = ps.stem(word.lower(), 0, len(word)-1)
                    # print(stemmed)
                    if(len(postings[stemmed])==0):
                        postings[stemmed].append(count)
                        lastDoc[stemmed]=count   
                    elif(lastDoc[stemmed]!=count):
                        postings[stemmed].append(count-lastDoc[stemmed]) 
                        lastDoc[stemmed]=count       
        if(len(texts)>0):                        
            for text in texts:
                temp = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?\s]', text.get_text().lower())
                for word in temp:
                    stemmed = ps.stem(word.lower(), 0, len(word)-1)
                    # print(stemmed)
                    if(len(postings[stemmed])==0):
                        postings[stemmed].append(count) 
                        lastDoc[stemmed]=count   
                    elif(lastDoc[stemmed]!=count):
                        postings[stemmed].append(count-lastDoc[stemmed]) 
                        lastDoc[stemmed]=count  

byteCount = 0
cOffset = 0
destFile = open("c2_index_gap.idx", "wb")
for key in postings.keys():
    offsets[key]=cOffset
    pl = postings[key]
    toWrite = ''
    for post in pl:
        toWrite+=C2Encode(post)
    # print(toWrite)
    padding = (8 - (len(toWrite)%8))%8
    toWrite+=('1'*padding)
    bytesList = [toWrite[i:i+8] for i in range(0, len(toWrite), 8)]
    bytesList = [int(ele, 2) for ele in bytesList]
    # print(bytesList)
    cOffset+=len(bytesList)
    lenpl[key]=len(bytesList)
    for posting in bytesList:
        finalToWrite = posting.to_bytes(1, sys.byteorder)
        destFile.write(finalToWrite)

with open("c2_offsets", "w") as fp:
    json.dump(offsets,fp) 

with open("c2_lenpl", "w") as fp:
    json.dump(lenpl,fp) 

with open("c2_docid", "w") as fp:
    json.dump(docId,fp) 
