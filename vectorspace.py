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
    index[2][docid] = {}
    for token in set(tokens):
        if index[0].get(token) == None:
            index[0][token] = []
        index[0][token].append([docid, tokens.count(token)])
        index[1][docid][token] = tokens.count(token)
    return index

def weighTermTop(token, index, data, wscheme, c, memory):
    w = 1.0
    if memory.get(token) != None:
        return memory[token][0]
    if wscheme[0] == "t":
        w *= data
        maxtf = data
        for token in c:
            if c[token] > maxtf:
                maxtf = c[token]
        w /= maxtf
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
    memory[token] = []
    memory[token].append(w)
    return w

def weighTerm(token, index, data, wscheme, c, memory):
    if wscheme == "tfidx":
        wscheme = "tfx"
    if memory.get(token) != None and len(memory[token]) == 2:
        return memory[token][1]
    w = weighTermTop(token, index, data, wscheme, c, memory)
    if wscheme[2] == "c" and index[0].get(token) != None:
        cosine = 0.0
        for token in c:
            termweight = weighTermTop(token, index, c[token], wscheme, c, memory)
            cosine += termweight * termweight
        w /= math.sqrt(cosine)
    memory[token].append(w)
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
    for doc in docs:
        for token in index[1][doc]:
            weighTerm(token, index, index[1][doc][token], docw, index[1][doc], index[2][doc])
    query = {}
    queryFreq = {}
    for token in set(tokens):
        queryFreq[token] = tokens.count(token)
    for token in set(tokens):
        weighTerm(token, index, tokens.count(token), queryw, queryFreq, query)
    cosinequery = 0.0
    for token in query:
        cosinequery += query[token] * query[token]
    cosinequery = math.sqrt(cosinequery)
    rank = []
    for doc in docs:
        weight = 0.0
        for token in set(tokens):
            if index[2][doc].get(token) == None:
                continue
            weight += query[token] * index[2][doc][token]
        cosinedoc = 0.0
        for token in index[2][doc]:
            cosinedoc += index[2][doc][token] * index[2][doc][token]
        cosinedoc = math.sqrt(cosinedoc)
        if cosinedoc == 0:
            continue
        weight /= (cosinedoc * cosinequery)
        rank.append([doc, weight])
    rank = sorted(rank, sortMostRelevant)
    return rank

def main(args):
    if len(args) != 5:
        print "incorrect command line arguments"
    global docid
    docid = 0
    preprocess.generateStopwords()
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