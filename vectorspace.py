#SCOTT BOMMARITO
#uniqname: zucchini
#ASSIGNMENT 2
#EECS 498 WN 2015

import preprocess
import math
from os import listdir
from os.path import isfile, join

docid = 0

def indexDocument(text, docw, queryw, index):
    global docid
    docid += 1
    tokens = preprocess.tokenizeText(text)
    for token in set(tokens):
        if index.get(token) == None:
            index[token] = [0, []]
        tokendata = index[token]
        tokendata[0] += 1
        tokendata[1].append([docid, tokens.count(token)])
    return index

def weighTermTop(token, index, data, wscheme):
    w = 1.0
    if wscheme[0] == "t":
        w *= data
    if wscheme[0] == "n":
        maxtf = data
        for i in range(0, index[token][0]):
            if index[token][0][i][1] > maxtf:
                maxtf = index[token][0][i][1]
        w = .5 + .5 * data / maxtf
    if wscheme[1] == "f":
        w *= math.log(docid / index[token][0], 2)
    if wscheme[1] == "p":
        w *= math.log((docid - index[token][0]) / index[token][0], 2)
    return w

def weighTerm(token, index, data, wscheme):
    if wscheme == "tfidx":
        wscheme = "tfx"
    w = weighTermTop(token, index, data, wscheme)
    if wscheme[2] == "c":
        sum = 0.0
        for i in range(0, index[token][0]):
            sum += weighTermTop(token, index, index[token][1][i][1], wscheme)
        w /= math.sqrt(sum)
    return w

def sortMostRelevant(x, y):
    if x[1] == y[1]:
        return 0
    if x[1] > y[1]:
        return -1
    return 1

def retrieveDocuments(query, index, docw, queryw):
    tokens = preprocess.tokenizeText(query)
    docs = set()
    docstokens = {}
    for token in set(tokens):
        if index.get(token) == None:
            continue
        for i in range(0, index[token][0]):
            doc = index[token][1][i][0]
            docs.add(doc)
            if docstokens.get(doc) == None:
                docstokens[doc] = []
            docstokens[doc].append(token)
    docws = {}
    for doc in docs:
        docws[doc] = {}
        for token in docstokens[doc]:
            data = 0
            for i in range(0, index[token][0]):
                if index[token][1][i][0] == doc:
                    data = index[token][1][i][1]
            docws[doc][token] = weighTerm(token, index, data, docw)
    query = {}
    for token in set(tokens):
        if index.get(token) == None:
            continue
        query[token] = weighTerm(token, index, tokens.count(token), queryw)
    rank = []
    for doc in docs:
        weight = 0.0
        for token in set(tokens):
            if index.get(token) == None or docws[doc].get(token) == None:
                continue
            weight += query[token] * docws[doc][token]
        cosinequery = 0.0
        for token in query:
            cosinequery += query[token] * query[token]
        cosinequery = math.sqrt(cosinequery)
        cosinedoc = 0.0
        for token in docws[doc]:
            cosinedoc += docws[doc][token] * docws[doc][token]
        cosinedoc = math.sqrt(cosinedoc)
        if cosinedoc == 0 or cosinequery == 0:
            continue
        weight = weight / (cosinedoc * cosinequery)
        rank.append([doc, weight])
    rank = sorted(rank, sortMostRelevant)
    return rank

def main(args):
    if len(args) != 5:
        print "incorrect command line arguments"
    docw = args[1]
    queryw = args[2]
    folder = args[3]
    files = [folder + filename for filename in listdir(folder) if isfile(join(folder, filename))]
    index = {}
    for filename in files:
        filein = open(filename)
        index = indexDocument(filein.read(), docw, queryw, index)
        filein.close()
    queryin = open(args[4])
    i = 0
    for line in queryin:
        i += 1
        for data in retrieveDocuments(line, index, docw, queryw):
            print str(i) + " " + str(data[0]) + " " + str(data[1])

def runVecTfidx():
    runVec("tfx", "tfx")
    
def runVec(docw, queryw):
    main([",", docw, queryw, "cranfieldDocs/", "cranfield.queries.test"])