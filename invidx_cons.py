from bs4 import BeautifulSoup
from PorterStemmer import PorterStemmer
from collections import defaultdict
import sys
import re
import snappy
import os
import json
import string
import time

def def_value():
    return "Not Present"

def c1_encode(n):
    byte_arr = [] 
    byte_arr.append(n%128)
    n = n//128
    while(True):
        if(n==0):           
            break
        else: 
            byte_arr.insert(0, n%128 + 128)
            n = n//128
    return byte_arr

def c2_encode(x):
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


if __name__ == '__main__':

    start = time.time()

    ps = PorterStemmer()
    docId = defaultdict(def_value)
    postings = defaultdict(list)
    count = 0
    lastDoc = defaultdict(int)
    offsetAndLength = defaultdict(lambda: [0,0])

    exclist = ',.:;"’(){}[]\n`\''
    table = str.maketrans(exclist, ' '*len(exclist), '')

    coll_path = sys.argv[1]
    index_file = sys.argv[2]
    stopword_file = sys.argv[3]
    c_no = int(sys.argv[4])
    xml_tags_info = sys.argv[5]

    if(c_no>=4):
        print('not implemented')
        exit()

    xmltags = []
    with open(xml_tags_info, 'r') as f:
        for line in f:
            temp = line.rstrip()
            if(temp!='DOCNO'):
                xmltags.append(temp.lower())
    
    stopwords = []
    with open(stopword_file, 'r') as f:
        for line in f:
            temp = line.rstrip()
            stopwords.append(temp.lower())
    # print(stopwords)

    filecount = 0
    doclist = os.listdir(coll_path)
    total = len(doclist)

    for file in doclist:
        filecount += 1
        f = os.path.join(coll_path, file)
        if(file=='ap890520'): 
            continue
        # if(filecount>5):
        #     break
        xmldoc = open(f, 'r')
        soup = BeautifulSoup(xmldoc, 'html.parser')
        docs = soup.find_all('doc')
        # print('Processing ', f, '( ', filecount, ' out of ', total, ' processed )')
        for doc in docs:
            count += 1
            docNo = doc.find('docno')
            # heads = doc.find_all('head')
            # texts = doc.find_all('text')
            id = docNo.get_text().replace(' ', '')
            docId[count] = id
            for xmltag in xmltags:
                tag_list = doc.find_all(xmltag)
                if(len(tag_list)>0):
                    for tag_obj in tag_list:
                        textBlob = tag_obj.get_text()
                        for stopword in stopwords:
                            textBlob.replace(stopword, '')
                        temp = textBlob.translate(str.maketrans(table)).split()
                        # temp = modText.split()
                        # temp = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>?\s]', head.get_text())
                        for word in temp:
                            if(word=='' or word==' ' or word=='  '):
                                continue
                            if(word in stopwords):
                                continue
                            stemmed = ps.stem(word.lower(), 0, len(word)-1)
                            # print(stemmed)
                            if(len(postings[stemmed])==0):
                                postings[stemmed].append(count)
                                lastDoc[stemmed]=count   
                            elif(lastDoc[stemmed]!=count):
                                postings[stemmed].append(count-lastDoc[stemmed]) 
                                lastDoc[stemmed]=count    

    destFile = open(index_file+'.idx', "wb")
    destFile.write(c_no.to_bytes(1, sys.byteorder))
    cOffset = 1
    encodedJSON = json.dumps(docId).encode('utf-8')
    destFile.write(encodedJSON)
    offsetAndLength['DocIdMapLength'][0] = 1
    offsetAndLength['DocIdMapLength'][1] = len(encodedJSON)
    cOffset += len(encodedJSON)
    offsetAndLength['Stopwords'][0] = cOffset
    if(len(stopwords)>0):
        sw_string = str(stopwords).encode()
        destFile.write(sw_string)
        offsetAndLength['Stopwords'][1] = len(sw_string)
        cOffset += len(sw_string)
    else: 
        offsetAndLength['Stopwords'][1] = 0
    # print(sw_string)
    # print(len(sw_string))

    if(c_no==0):
        for key in postings.keys():
            offsetAndLength[key][0]=cOffset
            pl = postings[key]
            toWrite=''
            for i in range(0,len(pl)):
                toWrite+=str(pl[i])
                if(i!=len(pl)-1):
                    toWrite+=','
            toWrite = toWrite.encode('utf8')
            cOffset+=len(toWrite)
            offsetAndLength[key][1]=len(toWrite)
            destFile.write(toWrite)
    elif(c_no==1):
        for key in postings.keys():
            offsetAndLength[key][0]=cOffset
            pl = postings[key]
            for post in pl:
                encoded = c1_encode(post)
                for j in range(0, len(encoded)):
                    toWrite = encoded[j].to_bytes(1, sys.byteorder)
                    cOffset+=1
                    offsetAndLength[key][1]+=1
                    destFile.write(toWrite)   
    elif(c_no==2):
        for key in postings.keys():
            offsetAndLength[key][0]=cOffset
            pl = postings[key]
            toWrite = ''
            for post in pl:
                toWrite+=c2_encode(post)
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
    elif(c_no==3):
        for key in postings.keys():
            offsetAndLength[key][0]=cOffset
            pl = postings[key]
            toWrite = ''
            for post in pl:
                toWrite+=str(post)
                toWrite+=','
            toWrite = toWrite.encode()
            toWrite=snappy.compress(toWrite)
            # print(toWrite)
            destFile.write(toWrite)
            cOffset+=len(toWrite)
            offsetAndLength[key][1]=len(toWrite)    
    elif(c_no==4):
        print('not implemented')
    elif(c_no==5):
        print('not_implemented')
    else: 
        print('not_implemented')   

    with open(index_file+'.dict', "w") as fp:
        json.dump(offsetAndLength,fp) 
    
    end = time.time()
    print(end - start)
