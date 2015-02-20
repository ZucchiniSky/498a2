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
    tokens = preprocess.processText(text)
    index[1][docid] = {}
    for token in set(tokens):
        if index[0].get(token) == None:
            index[0][token] = []
        index[0][token].append([docid, tokens.count(token)])
        index[1][docid][token] = tokens.count(token)
    return index

def weighTermTop(token, index, data, wscheme):
    w = 1.0
    if wscheme[0] == "t":
        w *= data
    if wscheme[0] == "n":
        maxtf = data
        for i in range(0, len(index[0][token])):
            if index[0][token][i][1] > maxtf:
                maxtf = index[0][token][i][1]
        w = .5 + .5 * data / maxtf
    if wscheme[1] == "f":
        if index[0].get(token) != None:
            w *= math.log(docid / len(index[0][token]), 10)
        else:
            w *= math.log(docid, 10)
    if wscheme[1] == "p":
        if index[0].get(token) != None:
            w *= math.log((docid - len(index[0][token])) / len(index[0][token]), 10)
        else:
            w *= math.log(docid - 1, 10)
    return w

def weighTerm(token, index, data, wscheme):
    if wscheme == "tfidx":
        wscheme = "tfx"
    w = weighTermTop(token, index, data, wscheme)
    if wscheme[2] == "c" and index[0].get(token) != None:
        sum = 0.0
        for i in range(0, len(index[0][token])):
            sum += weighTermTop(token, index, index[0][token][i][1], wscheme)
        w /= math.sqrt(sum)
    return w

def sortMostRelevant(x, y):
    if x[1] == y[1]:
        return 0
    if x[1] > y[1]:
        return -1
    return 1

def retrieveDocuments(query, index, docw, queryw):
    tokens = preprocess.processText(query)
    docs = set()
    docstokens = {}
    for token in set(tokens):
        if index[0].get(token) == None:
            continue
        for i in range(0, len(index[0][token])):
            doc = index[0][token][i][0]
            docs.add(doc)
            if docstokens.get(doc) == None:
                docstokens[doc] = []
            docstokens[doc].append(token)
    docws = {}
    for doc in docs:
        docws[doc] = {}
        for token in docstokens[doc]:
            data = 0
            for i in range(0, len(index[0][token])):
                if index[0][token][i][0] == doc:
                    data = index[0][token][i][1]
            docws[doc][token] = weighTerm(token, index, data, docw)
    query = {}
    for token in set(tokens):
        query[token] = weighTerm(token, index, tokens.count(token), queryw)
    cosinequery = 0.0
    for token in query:
        cosinequery += query[token] * query[token]
    cosinequery = math.sqrt(cosinequery)
    rank = []
    for doc in docs:
        weight = 0.0
        found = 0
        for token in set(tokens):
            if docws[doc].get(token) == None:
                continue
            found = 1
            weight += query[token] * docws[doc][token]
        if found == 0:
            continue
        cosinedoc = 0.0
        for token in set(tokens):
            if index[1][doc].get(token) == None:
                continue
            termweight = weighTerm(token, index, index[1][doc][token], docw)
            cosinedoc += termweight * termweight
        cosinedoc = math.sqrt(cosinedoc)
        if cosinedoc == 0:
            continue
        weight = weight / (cosinedoc * cosinequery)
        rank.append([doc, weight])
    rank = sorted(rank, sortMostRelevant)
    num = 0
    print str(0)
    print query
    for tuple in rank:
        print str(tuple[0]) + " " + str(tuple[1])
        print docws[tuple[0]]
        print index[1][tuple[0]]
        num += 1
        if num > 50:
            break
    return rank

def main(args):
    if len(args) != 5:
        print "incorrect command line arguments"
    docw = args[1]
    queryw = args[2]
    folder = args[3]
    files = [folder + filename for filename in listdir(folder) if isfile(join(folder, filename))]
    index = [{},{}]
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