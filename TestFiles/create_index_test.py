from bs4 import BeautifulSoup
from stemmer import PorterStemmer
from collections import defaultdict
import re

xmldoc = open('./tipster-ap-frac/ap880212', 'r').read()
soup = BeautifulSoup('<JAPNEET>' + xmldoc + '</JAPNEET>', 'xml')
ps = PorterStemmer()
docs = soup.find_all('DOC')
docId = {}
postings = defaultdict(list)
count = 0

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
                if(len(postings[stemmed])==0 or postings[stemmed][-1]!=count):
                    postings[stemmed].append(count)
        for text in texts:
            temp = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?\s]', text.get_text().lower())
            for word in temp:
                stemmed = ps.stem(word, 0, len(word)-1)
                # print(stemmed)
                if(len(postings[stemmed])==0 or postings[stemmed][-1]!=count):
                    postings[stemmed].append(count)                    


# print('DOC count: '+str(len(docs)))
# print('HEAD count: '+str(len(heads)))
# print(soup.original_encoding)
# print(type(xmldoc))

list1 = postings['i']
list2 = postings['simon']
len1 = len(list1)
len2 = len(list2)
i = 0
j = 0
print(list1)
print(list2)
while(i<len1 and j<len2):
    if(list1[i]==list2[j]):
        print(docId[list1[i]])
        i+=1
        j+=1
    elif(list1[i]<list2[j]):
        i+=1
    else: 
        j+=1
