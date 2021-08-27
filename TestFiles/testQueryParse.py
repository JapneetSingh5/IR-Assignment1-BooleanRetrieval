from PorterStemmer import PorterStemmer
ps = PorterStemmer()

queryfile = 'query.txt'
queries = []
with open(queryfile, 'r') as f:
    for line in f:
        temp = line.rstrip()
        tempList = temp.split()
        if(len(tempList)>0):
            queries.append(tempList)

for query in queries:
    for i in range(0, len(query)):
        query[i] = query[i].lower()
        query[i] = ps.stem(query[i], 0, len(query[i])-1)


print(queries)