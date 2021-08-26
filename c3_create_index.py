from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
import snappy
import sys
import re
import os
import json
import string

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
    # if(filecount>5):
    #     break
    xmldoc = open(f, 'r').read()
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
                # print(head.get_text())
                # temp = re.sub(r'[^\w\s]', '', head.get_text().lower())
                # temp = temp.split()
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
                # temp = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?\s]', text.get_text().lower()
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

destFile = open("c3_index_gap.idx", "wb")
encodedJSON = json.dumps(docId).encode('utf-8')
destFile.write(encodedJSON)
offsetAndLength['DocIdMapLength'] = len(encodedJSON)
cOffset = len(encodedJSON)

for key in postings.keys():
    offsetAndLength[key][0]=cOffset
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
    offsetAndLength[key][1]=len(toWrite)

with open("c3_offsetAndLength", "w") as fp:
    json.dump(offsetAndLength,fp) 