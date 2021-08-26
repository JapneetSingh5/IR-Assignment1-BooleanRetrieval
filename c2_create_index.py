from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
import sys
import re
import os
import json
import string

def C2Encode(x):
    encoded = ""
    lx = x.bit_length()
    llx = lx.bit_length()
    for _ in range(0, llx-1):
        encoded += '1'
    encoded += '0'
    a1 = lx
    b1 = llx-1
    temp1 = ""
    for _ in range(0,b1):
        temp1 = str(a1%2) + temp1
        a1 = a1//2
    a2 = x
    b2 = lx-1
    temp2 = ""
    for _ in range(0,b2):
        temp2 = str(a2%2) + temp2
        a2 = a2//2
    encoded += temp1
    encoded += temp2
    return encoded

exclist = string.punctuation 
table = str.maketrans('', '', exclist)

ps = PorterStemmer()
def def_value():
    return "Not Present"
docId = defaultdict(def_value)
postings = defaultdict(list)
count = 0
lastDoc = defaultdict(int)
offsets = defaultdict(int)
offsetAndLength = defaultdict(lambda: [0, 0])

filecount = 0
doclist = os.listdir('tipster-ap-frac')
total = len(doclist)
for file in doclist:
    filecount += 1
    f = os.path.join('tipster-ap-frac', file)
    if(file=='ap890520'): 
        continue
    # if(filecount>5):
    #     break    
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

destFile = open("c2_index_gap.idx", "wb")
encodedJSON = json.dumps(docId).encode('utf-8')
destFile.write(encodedJSON)
offsetAndLength['DocIdMapLength'] = len(encodedJSON)
cOffset = len(encodedJSON)

for key in postings.keys():
    offsetAndLength[key][0]=cOffset
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
    offsetAndLength[key][1]=len(bytesList)
    for posting in bytesList:
        finalToWrite = posting.to_bytes(1, sys.byteorder)
        destFile.write(finalToWrite)

with open("c2_offsetAndLength", "w") as fp:
    json.dump(offsetAndLength,fp) 
