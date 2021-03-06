from bs4 import BeautifulSoup
from stemmer import PorterStemmer
import re

xmldoc = open('./tipster-ap-frac/ap880212', 'r').read()
soup = BeautifulSoup('<JAPNEET>' + xmldoc + '</JAPNEET>', 'xml')
ps = PorterStemmer()
# print(soup)
docs = soup.find_all('DOC')

for doc in docs:
    docNo = doc.find('DOCNO')
    heads = doc.find_all('HEAD')
    if(len(heads)>0):
        print(docNo.get_text().replace(' ', ''))
        for head in heads:
            print(head.get_text())
            # temp = re.sub(r'[^\w\s]', '', head.get_text().lower())
            # temp = temp.split()
            temp = re.split('\s|(?<!\d)[,.]|[,.](?!\d)', head.get_text().lower())
            for word in temp:
                print(ps.stem(word, 0, len(word)-1))


# print('DOC count: '+str(len(docs)))
# print('HEAD count: '+str(len(heads)))
# print(soup.original_encoding)
# print(type(xmldoc))