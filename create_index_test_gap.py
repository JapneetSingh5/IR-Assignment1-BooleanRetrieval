from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
import pprint
import re

xmldoc = open('./tipster-ap-frac/ap880212', 'r').read()
soup = BeautifulSoup('<JAPNEET>' + xmldoc + '</JAPNEET>', 'xml')
ps = PorterStemmer()
docs = soup.find_all('DOC')
docId = {}
postings = defaultdict(list)
count = 0
lastDoc = defaultdict(int)
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
                               

list1 = postings['simon']
list2 = postings['i']
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
