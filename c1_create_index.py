from bs4 import BeautifulSoup
from PorterStemmer import PorterStemmer
from collections import defaultdict
import sys
import re
import os
import json
import string

def VBEncode(n):
    bytes = [] 
    bytes.append(n%128)
    n = n//128
    while(True):
        if(n==0):           
            break
        else: 
            bytes.insert(0, n%128 + 128)
            n = n//128
    return bytes

exclist = string.punctuation 
table = str.maketrans('', '', exclist)

ps = PorterStemmer()
def def_value():
    return "Not Present"
docId = defaultdict(def_value)
postings = defaultdict(list)
count = 0
lastDoc = defaultdict(int)
offsetAndLength = defaultdict(lambda: [0,0])

filecount = 0
doclist = sorted(os.listdir('tipster-ap-frac'))
total = len(doclist)
for file in doclist:
    filecount += 1
    f = os.path.join('tipster-ap-frac', file)
    if(file=='ap890520'): 
        continue
    if(filecount>20):
        break
    xmldoc = open(f, 'r')
    soup = BeautifulSoup(xmldoc, 'lxml')
    docs = soup.find_all('doc')
    print('Processing ', f, '( ', filecount, ' out of ', total, ' processed )')
    for doc in docs:
        count += 1
        docNo = doc.find('docno')
        heads = doc.find_all('head')
        texts = doc.find_all('text')
        id = docNo.get_text().replace(' ', '')
        docId[count] = id
        if(len(heads)>0):
            for head in heads:
                temp = head.get_text().translate(str.maketrans(table)).split()
                # temp = modText.split()
                # temp = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?\s]', head.get_text())
                for word in temp:
                    if(word=='' or word==' ' or word=='  ' or word.isnumeric()):
                        continue
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
                temp =text.get_text().translate(table).split()
                # temp = modText.split()
                # temp = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?\s]', text.get_text().lower())
                for word in temp:
                    if(word=='' or word==' ' or word=='  ' or word.isnumeric()):
                        continue
                    stemmed = ps.stem(word.lower(), 0, len(word)-1)
                    # print(stemmed)
                    if(len(postings[stemmed])==0):
                        postings[stemmed].append(count) 
                        lastDoc[stemmed]=count   
                    elif(lastDoc[stemmed]!=count):
                        postings[stemmed].append(count-lastDoc[stemmed]) 
                        lastDoc[stemmed]=count  

destFile = open("c1_index_gap.idx", "wb")
encodedJSON = json.dumps(docId).encode('utf-8')
destFile.write(encodedJSON)
offsetAndLength['DocIdMapLength'] = len(encodedJSON)
cOffset = len(encodedJSON)

for key in postings.keys():
    offsetAndLength[key][0]=cOffset
    pl = postings[key]
    for post in pl:
        encoded = VBEncode(post)
        for j in range(0, len(encoded)):
            toWrite = encoded[j].to_bytes(1, sys.byteorder)
            cOffset+=1
            offsetAndLength[key][1]+=1
            destFile.write(toWrite)

with open("c1_offsetAndLength", "w") as fp:
    json.dump(offsetAndLength,fp) 


