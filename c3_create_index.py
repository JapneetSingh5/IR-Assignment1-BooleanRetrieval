from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
import snappy
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
    iter+=1
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
                # print(head.get_text())
                # temp = re.sub(r'[^\w\s]', '', head.get_text().lower())
                # temp = temp.split()
                temp = re.split('\s|(?<!\d)[,.]|[,.](?!\d)', head.get_text())
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
destFile = open("c3_index_gap.idx", "wb")
for key in postings.keys():
    offsets[key]=cOffset
    pl = postings[key]
    toWrite = ''
    for post in pl:
        toWrite+=str(post)
        toWrite+=' '
    toWrite = toWrite.encode()
    toWrite=snappy.compress(toWrite)
    # print(toWrite)
    destFile.write(toWrite)
    cOffset+=len(toWrite)
    lenpl[key]=len(toWrite)

with open("c3_offsets", "w") as fp:
    json.dump(offsets,fp) 

with open("c3_lenpl", "w") as fp:
    json.dump(lenpl,fp) 

with open("c3_docid", "w") as fp:
    json.dump(docId,fp) 
