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

def write_dict_to_file(d, file, logDict, lastDoc):
    cOffset = 0
    with open(file, 'wb') as f:
        for term in d.keys():
            pl = d[term]
            toWrite=''
            for i in range(0,len(pl)):
                toWrite+=str(pl[i])
                if(i!=len(pl)-1):
                    toWrite+=','
            toWrite = toWrite.encode('utf8')
            logDict[term][0]=cOffset
            logDict[term][1] = len(toWrite)
            cOffset += len(toWrite)
            f.write(toWrite)
    return logDict


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
    doclist = sorted(os.listdir(coll_path))
    # print(doclist)
    total = len(doclist)

    block_size = 100
    sub_index_no = 1
    temp_indexfile = 'tempindex'
    temp_dictfile = 'tempdictfile'
    temp_olfile = 'tempol'
    id_term_map = {}
    tempOL = defaultdict(lambda: [0,0])



    for file in doclist:
        filecount += 1
        f = os.path.join(coll_path, file)
        if(file=='ap890520'): 
            continue
        if(filecount>5):
            break
        xmldoc = open(f, 'r')
        soup = BeautifulSoup(xmldoc, 'html.parser')
        docs = soup.find_all('doc')
        print('Processing ', f, '( ', filecount, ' out of ', total, ' processed )')
        for doc in docs:
            count += 1
            docNo = doc.find('docno')
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
                            if(word=='' or word==' ' or word=='  ' or word.isnumeric()):
                                continue
                            if(word in stopwords):
                                continue
                            stemmed = ps.stem(word.lower(), 0, len(word)-1)
                            if(stemmed not in offsetAndLength):
                                offsetAndLength[stemmed][0]=0
                                offsetAndLength[stemmed][1]=0
                            if(len(postings[stemmed])==0):
                                postings[stemmed].append(count)
                                lastDoc[stemmed]=count   
                            elif(lastDoc[stemmed]!=count):
                                postings[stemmed].append(count-lastDoc[stemmed]) 
                                lastDoc[stemmed]=count 
        if(filecount%block_size==0):
            tempOL = write_dict_to_file(postings, temp_indexfile+str(sub_index_no), tempOL, lastDoc)
            postings.clear()
            with open(temp_olfile +str(sub_index_no), 'wb') as f:
                sub_index_OL = json.dumps(tempOL)
                f.write(sub_index_OL.encode())
            tempOL.clear()
            sub_index_no+=1
    if(len(postings)>0):
            tempOL = write_dict_to_file(postings, temp_indexfile+str(sub_index_no), tempOL, lastDoc)
            postings.clear()
            with open(temp_olfile +str(sub_index_no), 'wb') as f:
                sub_index_OL = json.dumps(tempOL)
                f.write(sub_index_OL.encode())
            tempOL.clear()
    print('Total', sub_index_no, ' subindices created. Going for merge and compress..')


    destFile = open(index_file+'.idx', "wb")
    destFile.write(c_no.to_bytes(1, sys.byteorder))
    cOffset = 1
    encodedJSON = json.dumps(docId).encode('utf-8')
    destFile.write(encodedJSON)
    offsetAndLength['DocIdMapLength'][0] = 1
    offsetAndLength['DocIdMapLength'][1] = len(encodedJSON)
    cOffset += len(encodedJSON)

    if(c_no==0):
        tempols = []
        fs=[]
        for i in range(1, sub_index_no + 1):
            f = open(temp_olfile+str(i), 'rb')
            tempOL = json.load(f)
            tempols.append(tempOL)
        for i in range(1, sub_index_no + 1):
            f = open(temp_indexfile+str(i), 'rb')
            fs.append(f)
        for key in offsetAndLength.keys():
            if(key=='DocIdMapLength'):
                continue
            offsetAndLength[key][0]=cOffset
            fullToWrite=''
            for i in range(0, sub_index_no):
                if(key not in tempols[i]):
                    continue
                offset = tempols[i][key][0]
                readLen = tempols[i][key][1]
                subIndex = fs[i]
                subIndex.seek(offset)
                subList = subIndex.read(readLen)
                if(i>1):
                    toWrite=','.encode()+subList
                    destFile.write(','.encode()+subList)
                    cOffset+=len(toWrite)
                    offsetAndLength[key][1]+=len(toWrite)
                else: 
                    destFile.write(subList)
                    cOffset+=len(subList)
                    offsetAndLength[key][1]+=len(subList)
    elif(c_no==1):
        tempols = []
        fs=[]
        for i in range(1, sub_index_no + 1):
            f = open(temp_olfile+str(i), 'rb')
            tempOL = json.load(f)
            tempols.append(tempOL)
        for i in range(1, sub_index_no + 1):
            f = open(temp_indexfile+str(i), 'rb')
            fs.append(f)
        for key in offsetAndLength.keys():
            if(key=='DocIdMapLength'):
                continue
            offsetAndLength[key][0]=cOffset
            for i in range(0, sub_index_no):
                if(key not in tempols[i]):
                    continue
                offset = tempols[i][key][0]
                readLen = tempols[i][key][1]
                subIndex = fs[i]
                subIndex.seek(offset)
                subList = subIndex.read(readLen).decode()
                subList = subList.split(',')
                subList = [int(ele) for ele in subList]
                for post in subList:
                    encoded = c1_encode(post)
                    for j in range(0, len(encoded)):
                        toWrite = encoded[j].to_bytes(1, sys.byteorder)
                        cOffset+=1
                        offsetAndLength[key][1]+=1
                        destFile.write(toWrite)  
    elif(c_no==2):
        tempols = []
        fs=[]
        for i in range(1, sub_index_no + 1):
            f = open(temp_olfile+str(i), 'rb')
            tempOL = json.load(f)
            tempols.append(tempOL)
        for i in range(1, sub_index_no + 1):
            f = open(temp_indexfile+str(i), 'rb')
            fs.append(f)
        for key in offsetAndLength.keys():
            pl = []
            if(key=='DocIdMapLength'):
                continue
            offsetAndLength[key][0]=cOffset
            for i in range(0, sub_index_no):
                if(key not in tempols[i]):
                    continue
                offset = tempols[i][key][0]
                readLen = tempols[i][key][1]
                subIndex = fs[i]
                subIndex.seek(offset)
                subList = subIndex.read(readLen).decode()
                subList = subList.split(',')
                subList = [int(ele) for ele in subList]
                pl.extend(subList)
                toWrite=''
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
        tempols = []
        fs=[]
        for i in range(1, sub_index_no + 1):
            f = open(temp_olfile+str(i), 'rb')
            tempOL = json.load(f)
            tempols.append(tempOL)
        for i in range(1, sub_index_no + 1):
            f = open(temp_indexfile+str(i), 'rb')
            fs.append(f)
        for key in offsetAndLength.keys():
            pl = []
            if(key=='DocIdMapLength'):
                continue
            offsetAndLength[key][0]=cOffset
            for i in range(0, sub_index_no):
                if(key not in tempols[i]):
                    continue
                offset = tempols[i][key][0]
                readLen = tempols[i][key][1]
                subIndex = fs[i]
                subIndex.seek(offset)
                subList = subIndex.read(readLen).decode()
                subList = subList.split(',')
                subList = [int(ele) for ele in subList]
                pl.extend(subList)
                toWrite=''
                for post in pl:
                    toWrite+=c2_encode(post)
                # print(toWrite)
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
