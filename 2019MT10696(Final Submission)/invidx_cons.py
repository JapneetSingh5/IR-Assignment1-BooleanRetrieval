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
    #default value for docId->docNO mapping dictionary, ideally shold never be needed
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
    #input: a postings list 
    #output: encoding of the postings list, in string form
    b = pl[0]
    maxEle = pl[0]
    k = 2
    cutOff = 0
    if(len(pl)==1):
        comp1 = ['{0:08b}'.format(x) for x in c1_encode(b)]
        comp2 = ['{0:08b}'.format(x) for x in c1_encode(k)]
        return(''.join(comp1)+''.join(comp2)+'11')
    while(cutOff<len(pl) and (cutOff+1)*100/len(pl)<80):
        b = min(b, pl[cutOff])
        maxEle = max(maxEle, pl[cutOff])
        cutOff += 1
    if(len(pl)>1):
        k = math.floor(math.log2(maxEle-b+2)) + 1
    while(cutOff<len(pl)):
        if(pl[cutOff]<=maxEle and pl[cutOff]>=b):
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
        to_write = comp1+comp2+comp3
        return to_write
    else: 
        comp4 = [['{0:08b}'.format(x) for x in c1_encode(ele)] for ele in pl[cutOff:]]
        comp4 = ''.join([''.join(x) for x in comp4])
        to_write = comp1+comp2+comp3+('1'*k)+comp4
        return to_write


# write_to_dict_c<0|1|2|3> functions are used only while writing to sub-inverted index files
# the final write to <indexfile>.idx is managed seperately at the end
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

# this function is used only while writing to sub-inverted index files
# the final write to <indexfile>.idx is managed seperately at the end
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
    # start the timer
    # start = time.time()
    # Porter Stemmer Object
    ps = PorterStemmer()
    # docId (int) -> docNo (str) map
    docId = defaultdict(def_value)
    # dictionary containing postings list, word (str) -> postings (list) map
    postings = defaultdict(list)
    # count maintains the number of documents processed (not files)
    count = 0
    # filecount maintains the number of files processed
    filecount = 0
    # lastDoc maintains the id of lastDoc every word in the vocabulary appeared in
    lastDoc = defaultdict(lambda: 0)
    # offsetAndLength acts as the dictionary, stores the file offset and length of list where the list is stored in the index
    offsetAndLength = {}
    # delimiter list 
    exclude = ',.:;"(){}[]\n`\''
    table = str.maketrans(exclude, ' '*len(exclude), '')
    stopword_dict = defaultdict(lambda: 0)
    # processing command line arguments
    coll_path = sys.argv[1]
    index_file = sys.argv[2]
    stopword_file = sys.argv[3]
    c_no = int(sys.argv[4])
    xml_tags_info = sys.argv[5]
    # check for non implemented compression schemes or invalid inputs\        
    not_implemented = 'not implemented'
    if(c_no==4 or c_no>5 or c_no<0):
        print(not_implemented)
        exit()
    # get the list of xml tags to be indexed from xml_tags_info file, leave out DOCNO
    xmltags = []
    with open(xml_tags_info, 'r') as f:
        for line in f:
            temp = line.rstrip()
            if(temp!='DOCNO'):
                xmltags.append(temp.lower())
    # get the list of stopwords to remain unindexed from stopwords file
    stopwords = []
    with open(stopword_file, 'r') as f:
        for line in f:
            temp = line.rstrip()
            stopwords.append(temp.lower())
            stopword_dict[temp.lower()] = 1
    # get list of files to be processed and their count
    doclist = sorted(os.listdir(coll_path))
    total = len(doclist)
    # block size is the number of FILES to be processed per sub-index, make it 700 for submission
    block_size = 700
    sub_index_no = 1
    temp_indexfile = 'C'+str(c_no)+'tempindex'
    temp_olfile = 'C'+str(c_no)+'tempol'
    tempOL = defaultdict(lambda: [0,0])

    for file in doclist:
        filecount += 1
        f = os.path.join(coll_path, file)
        # UNSKIP THIS FILE IF IT IS ENSURED THAT IS ASCII-ENCODED, ELSE SKIP IT
        # if(file=='ap890520'): 
        #     continue
        # to create smaller indices, only for testing purposes
        xmldoc = open(f, 'r')
        soup = BeautifulSoup(xmldoc, 'html.parser')
        # create list of all docs in the current file by searching <DOC> tags
        docs = soup.find_all('doc')
        # print('Processing ', f, '( ', filecount, ' out of ', total, ' processed )')
        for doc in docs:
            count += 1
            # get DOCNO, i.e. the unique identifier for given doc
            docNo = doc.find('docno')
            # some docno are padded by spaces within DOCNO tags, remove the extra whitespace
            id = docNo.get_text().replace(' ', '')
            # DOCID, an integer -> DOCNO, a string
            docId[count] = id
            # iterate through xml tags in the xml tags list
            for xmltag in xmltags:
                # find all matching tags in the current DOC
                tag_list = doc.find_all(xmltag)
                if(len(tag_list)>0):
                    for tag_obj in tag_list:
                        textBlob = tag_obj.get_text()
                        # remove stopwords
                        for stopword in stopwords:
                            textBlob.replace(stopword, '')
                        # split at delimiters
                        temp = textBlob.translate(str.maketrans(table)).split()
                        for word in temp:
                            if(word=='' or word==' ' or word=='  '):
                                continue
                            # stem word using porter stemmer
                            stemmed = ps.stem(word.lower(), 0, len(word)-1)
                            if(stopword_dict[stemmed]==1):
                                continue
                            if(lastDoc[stemmed]==0):
                                # term has been encountered for the first time, give current docId as its element in the list
                                offsetAndLength[stemmed] = [0,0]
                                postings[stemmed].append(count)
                                lastDoc[stemmed]=count   
                            elif(lastDoc[stemmed]!=count):
                                # term has been encountered before, append gap to postings list
                                postings[stemmed].append(count-lastDoc[stemmed]) 
                                lastDoc[stemmed]=count 
        # if we reach block size limit, write the sub-invindex and sub-dictionary to a file
        if(filecount%block_size==0):
            tempOL = write_dict_to_file(c_no, postings, temp_indexfile+str(sub_index_no), tempOL)            
            postings.clear()
            with open(temp_olfile +str(sub_index_no), 'wb') as f:
                sub_index_OL = json.dumps(tempOL)
                f.write(sub_index_OL.encode())
            tempOL.clear()
            sub_index_no+=1
    # if postings list is non empty, write the sub-invindex and sub-dictionary to a file
    if(len(postings)>0):
        tempOL = write_dict_to_file(c_no, postings, temp_indexfile+str(sub_index_no), tempOL) 
        postings.clear()
        with open(temp_olfile +str(sub_index_no), 'wb') as f:
            sub_index_OL = json.dumps(tempOL)
            f.write(sub_index_OL.encode())
        tempOL.clear()

    #now, merge the sub-inv indices created till now to <indexfile>.idx and create an overall dictionary
    destFile = open(index_file+'.idx', "wb")
    destFile.write(c_no.to_bytes(1, sys.byteorder))
    c_offset = 1

    offsetAndLength['DocIdMapLength'] = docId

    # list of file pointers for sub-indices
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

    # compress and write to file according to the required c_no
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
            to_write = c5_encode(pl)
            padding = (8 - (len(to_write)%8))%8
            to_write+=('1'*padding)
            bytesList = [to_write[i:i+8] for i in range(0, len(to_write), 8)]
            bytesList = [int(ele, 2) for ele in bytesList]
            c_offset+=len(bytesList)
            offsetAndLength[key][1]=len(bytesList)
            destFile.write(bytearray(bytesList))                 
    else: 
        print(not_implemented)   

    # write dictionary to <indexfile>.dict filee
    with open(index_file+'.dict', "w") as fp:
        json.dump(offsetAndLength,fp) 
    # close all open file objects
    for i in range(0, len(fs)):
        fs[i].close()
    # check end time and print elapsed time
    # end = time.time()
    # print(end - start)
