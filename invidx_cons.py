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
import math

def def_value():
    #default value for docId->doc mapping dictionary, ideally shold never be needed
    return "Not Present"

def c1_encode(n):
    #input: an integer n
    #output: an array of int, each int the decimal representation of each byte in n's encoding
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
    #input: integer n
    #output: a string representation of encoding of n
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

def c5_encode(pl):
    b = pl[0]
    maxEle = pl[0]
    k = 2
    cutOff = 0
    if(len(pl)==1):
        comp1 = ['{0:08b}'.format(x) for x in c1_encode(b)]
        comp2 = ['{0:08b}'.format(x) for x in c1_encode(k)]
        return(''.join(comp1)+''.join(comp2)+'11'*(cutOff+1))
        # print(b,k,['{0:08b}'.format(x) for x in c1_encode(b)])
    while(cutOff<len(pl) and (cutOff+1)*100/len(pl)<80):
        b = min(b, pl[cutOff])
        # k = max(math.floor(math.log2(pl[cutOff]-b)) + 1, k)
        maxEle = max(maxEle, pl[cutOff])
        # print(cutOff)
        cutOff += 1
    if(len(pl)>1):
        k = math.floor(math.log2(maxEle-b+2)) + 1
    while(cutOff<len(pl)):
        if(pl[cutOff]<=maxEle and pl[cutOff]>=b):
        # print(pl[cutOff], pl[cutOff]-b, math.floor(math.log2(pl[cutOff]-b)) + 1, k)
            cutOff+=1
        elif(pl[cutOff]<b and math.floor(math.log2(maxEle-pl[cutOff]+2)) + 1 == k):
            b=pl[cutOff]
            cutOff+=1
        elif(pl[cutOff]>maxEle and math.floor(math.log2(pl[cutOff]-b+2)) + 1 == k):
            maxEle = pl[cutOff]
            cutOff+=1
        else: 
            break
    format_k = '{0:0'+str(k)+'b}'
    comp1 = ''.join(['{0:08b}'.format(x) for x in c1_encode(b)])
    comp2 = ''.join(['{0:08b}'.format(x) for x in c1_encode(k)])
    comp3 = ''.join([format_k.format(x-b) for x in pl[0:cutOff]])
    if(cutOff==len(pl)):
        # print(b,k,['{0:08b}'.format(x) for x in c1_encode(b)], ['{0:08b}'.format(x) for x in c1_encode(cutOff+1)], ['{0:06b}'.format(x-b) for x in pl[1:cutOff]])
        to_write = comp1+comp2+comp3
        padding = (8 - (len(to_write)%8))%8
        return to_write+('1'*padding)
    else: 
        # print(b,k,['{0:08b}'.format(x) for x in c1_encode(b)], ['{0:08b}'.format(x) for x in c1_encode(cutOff+1)], ['{0:06b}'.format(x-b) for x in pl[1:cutOff]], pl[cutOff:])
        # print(pl[cutOff:])
        comp4 = [['{0:08b}'.format(x) for x in c1_encode(ele)] for ele in pl[cutOff:]]
        comp4 = ''.join([''.join(x) for x in comp4])
        # print(comp4)
        to_write = comp1+comp2+comp3+('1'*k)+comp4
        padding = (8 - (len(to_write)%8))%8
        return to_write+('1'*padding)
    # comp1 = ['{0:08b}'.format(x) for x in c1_encode(b)]
    # comp2 = ['{0:08b}'.format(x) for x in c1_encode(k)]
    # comp3 = ['{0:06b}'.format(x-b) for x in pl[1:cutOff]]
    # return(''.join(comp1)+''.join(comp2)+''.join(comp3))


def write_dict_to_file_c0(d, file, log_dict):
    c_offset = 0
    with open(file, 'wb') as f:
        for term in d.keys():
            pl = d[term]
            to_write= ','.join([str(post) for post in pl])
            to_write = to_write.encode('utf8')
            log_dict[term][0]=c_offset
            log_dict[term][1] = len(to_write)
            c_offset += len(to_write)
            f.write(to_write)
    return log_dict

def write_dict_to_file_c1(d, file, log_dict):
    c_offset = 0
    with open(file, 'wb') as f:
        for term in d.keys():
            log_dict[term][0]=c_offset
            pl = d[term]
            for post in pl:
                encoded = c1_encode(post)
                for j in range(0, len(encoded)):
                    to_write = encoded[j].to_bytes(1, sys.byteorder)
                    c_offset+=1
                    log_dict[term][1]+=1
                    f.write(to_write)   
    return log_dict

def write_dict_to_file_c2(d, file, log_dict):
    c_offset = 0
    with open(file, 'wb') as f:
        for term in d.keys():
            pl = d[term]
            to_write=''
            for i in range(0,len(pl)):
                to_write+=c2_encode(pl[i])
            to_write = to_write.encode('utf8')
            log_dict[term][0] = c_offset
            log_dict[term][1] = len(to_write)
            c_offset += len(to_write)
            f.write(to_write)
    return log_dict

def write_dict_to_file_c3(d, file, log_dict):
    c_offset = 0
    with open(file, 'wb') as f:
        for term in d.keys():
            pl = d[term]
            to_write=''
            for i in range(0,len(pl)):
                to_write+=str(pl[i])
                if(i!=len(pl)-1):
                    to_write+=','
            to_write = to_write.encode('utf8')
            log_dict[term][0]= c_offset
            log_dict[term][1] = len(to_write)
            c_offset += len(to_write)
            f.write(to_write)
    return log_dict

def write_dict_to_file(c_no, d, file, log_dict):
    if(c_no==0):
        return write_dict_to_file_c0(d, file, log_dict)
    elif(c_no==1):
        return write_dict_to_file_c1(d, file, log_dict)
    elif(c_no==2):
        return write_dict_to_file_c2(d, file, log_dict)
    elif(c_no==3):
        return write_dict_to_file_c3(d, file, log_dict)
    elif(c_no==4):
        return {}
    elif(c_no==5):
        return write_dict_to_file_c0(d, file, log_dict)
    else: 
        return {}
    


if __name__ == '__main__':

    start = time.time()

    ps = PorterStemmer()
    docId = defaultdict(def_value)
    postings = defaultdict(list)
    count = 0
    lastDoc = defaultdict(lambda: 0)
    offsetAndLength = {}
    
    not_implemented = 'not implemented'
    exclist = ',.:;"(){}[]\n`\''
    table = str.maketrans(exclist, ' '*len(exclist), '')

    coll_path = sys.argv[1]
    index_file = sys.argv[2]
    stopword_file = sys.argv[3]
    c_no = int(sys.argv[4])
    xml_tags_info = sys.argv[5]

    if(c_no==4 or c_no>5 or c_no<0):
        print(not_implemented)
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

    filecount = 0
    doclist = sorted(os.listdir(coll_path))
    total = len(doclist)

    block_size = 100
    sub_index_no = 1
    temp_indexfile = 'C'+str(c_no)+'tempindex'
    temp_dictfile = 'C'+str(c_no)+'tempdictfile'
    temp_olfile = 'C'+str(c_no)+'tempol'
    tempOL = defaultdict(lambda: [0,0])

    for file in doclist:
        filecount += 1
        f = os.path.join(coll_path, file)
        if(file=='ap890520'): 
            continue
        # if(filecount<600):
        #     continue
        if(filecount>4):
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
                        for word in temp:
                            if(word=='' or word==' ' or word=='  '):
                                continue
                            if(word in stopwords):
                                continue
                            stemmed = ps.stem(word.lower(), 0, len(word)-1)
                            if(lastDoc[stemmed]==0):
                                # term has been encountered for the first time, give current docId as its element in the list
                                offsetAndLength[stemmed] = [0,0]
                                postings[stemmed].append(count)
                                lastDoc[stemmed]=count   
                            elif(lastDoc[stemmed]!=count):
                                # term has been encountered before
                                postings[stemmed].append(count-lastDoc[stemmed]) 
                                lastDoc[stemmed]=count 
        if(filecount%block_size==0):
            tempOL = write_dict_to_file(c_no, postings, temp_indexfile+str(sub_index_no), tempOL)            
            postings.clear()
            with open(temp_olfile +str(sub_index_no), 'wb') as f:
                sub_index_OL = json.dumps(tempOL)
                f.write(sub_index_OL.encode())
            tempOL.clear()
            sub_index_no+=1

    if(len(postings)>0):
        tempOL = write_dict_to_file(c_no, postings, temp_indexfile+str(sub_index_no), tempOL) 
        postings.clear()
        with open(temp_olfile +str(sub_index_no), 'wb') as f:
            sub_index_OL = json.dumps(tempOL)
            f.write(sub_index_OL.encode())
        tempOL.clear()

    destFile = open(index_file+'.idx', "wb")
    destFile.write(c_no.to_bytes(1, sys.byteorder))
    c_offset = 1
    # encodedJSON = json.dumps(docId).encode('utf-8')
    # destFile.write(encodedJSON)
    # json.dump(docId, destFile)
    offsetAndLength['DocIdMapLength'] = docId
    # offsetAndLength['DocIdMapLength'] = [1, destFile.tell()]
    # c_offset += destFile.tell()

    tempols = []
    fs=[]
    for i in range(1, sub_index_no + 1):
        if(os.path.isfile(temp_olfile+str(i))):
            f = open(temp_olfile+str(i), 'rb')
            tempOL = json.load(f)
            tempols.append(tempOL)
        f.close()
    for i in range(1, sub_index_no + 1):
        if(os.path.isfile(temp_indexfile+str(i))):
            f = open(temp_indexfile+str(i), 'rb')
            fs.append(f)

    if(c_no==0):
        for key in offsetAndLength.keys():
            if(key=='DocIdMapLength'):
                continue
            offsetAndLength[key][0]=c_offset
            printed=0
            bin_comma = ','.encode()
            for i in range(0, len(tempols)):
                if(key not in tempols[i]):
                    continue
                offset = tempols[i][key][0]
                readLen = tempols[i][key][1]
                subIndex = fs[i]
                subIndex.seek(offset)
                subList = subIndex.read(readLen)
                if(printed>0):
                    destFile.write(bin_comma)
                    c_offset+=len(bin_comma)
                    offsetAndLength[key][1]+=len(bin_comma)
                destFile.write(subList)
                c_offset+=len(subList)
                offsetAndLength[key][1]+=len(subList)
                printed+=1
    elif(c_no==1):
        for key in offsetAndLength.keys():
            if(key=='DocIdMapLength'):
                continue
            offsetAndLength[key][0]=c_offset
            for i in range(0, len(tempols)):
                if(key not in tempols[i]):
                    continue
                offset = tempols[i][key][0]
                readLen = tempols[i][key][1]
                subIndex = fs[i]
                subIndex.seek(offset)
                subList = subIndex.read(readLen)
                c_offset+=len(subList)
                offsetAndLength[key][1]+=len(subList)
                destFile.write(subList)  
    elif(c_no==2):
        for key in offsetAndLength.keys():
            pl = []
            if(key=='DocIdMapLength'):
                continue
            offsetAndLength[key][0]=c_offset
            to_write=''
            for i in range(0, len(tempols)):
                if(key not in tempols[i]):
                    continue
                offset = tempols[i][key][0]
                readLen = tempols[i][key][1]
                subIndex = fs[i]
                subIndex.seek(offset)
                subList = subIndex.read(readLen).decode('utf-8')
                to_write+=subList
            padding = (8 - (len(to_write)%8))%8
            to_write+=('1'*padding)
            bytesList = [to_write[i:i+8] for i in range(0, len(to_write), 8)]
            bytesList = [int(ele, 2) for ele in bytesList]
            c_offset+=len(bytesList)
            offsetAndLength[key][1]=len(bytesList)
            for posting in bytesList:
                finalto_write = posting.to_bytes(1, sys.byteorder)
                destFile.write(finalto_write) 
    elif(c_no==3):
        for key in offsetAndLength.keys():
            if(key=='DocIdMapLength'):
                continue
            to_write = ''
            offsetAndLength[key][0]=c_offset
            printed=0
            for i in range(0, len(tempols)):
                if(key not in tempols[i]):
                    continue
                offset = tempols[i][key][0]
                readLen = tempols[i][key][1]
                subIndex = fs[i]
                subIndex.seek(offset)
                subList = subIndex.read(readLen)
                subList=subList.decode()
                if(printed>0):
                    to_write+=','
                to_write+=subList
                printed+=1
            to_write=snappy.compress(to_write.encode())
            destFile.write(to_write)
            c_offset+=len(to_write)
            offsetAndLength[key][1]=len(to_write)     
    elif(c_no==4):
        print(not_implemented)
    elif(c_no==5):
        for key in offsetAndLength.keys():
            if(key=='DocIdMapLength'):
                continue
            offsetAndLength[key][0]=c_offset
            pl = []
            for i in range(0, len(tempols)):
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
            print(pl)
            to_write = c5_encode(pl)
            print(to_write)
            padding = (8 - (len(to_write)%8))%8
            to_write+=('1'*padding)
            # print(to_write)
            bytesList = [to_write[i:i+8] for i in range(0, len(to_write), 8)]
            bytesList = [int(ele, 2) for ele in bytesList]
            c_offset+=len(bytesList)
            offsetAndLength[key][1]=len(bytesList)
            destFile.write(bytearray(bytesList)) 
            print(key, 'done')                      
    else: 
        print(not_implemented)   

    print('out')
    with open(index_file+'.dict', "w") as fp:
        json.dump(offsetAndLength,fp) 

    for i in range(0, len(fs)):
        fs[i].close()
    
    end = time.time()
    print(end - start)
