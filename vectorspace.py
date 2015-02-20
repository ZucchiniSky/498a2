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
    index[2][docid] = [0, {}]
    for token in set(tokens):
        if index[0].get(token) is None:
            index[0][token] = []
        count = tokens.count(token)
        index[0][token].append([docid, count])
        index[1][docid][token] = count
        if count > index[2][docid][0]:
            index[2][docid][0] = count
    return index

def weighTermTop(token, index, data, wscheme, c, memory):
    w = 1.0
    if memory[1].get(token) is not None:
        return memory[1][token][0], memory
    if wscheme[0] == "t":
        w *= data
    if wscheme[0] == "n":
        w = .5 + .5 * data / memory[0]
    if wscheme[1] == "f":
        if index[0].get(token) is not None:
            w *= math.log(docid / len(index[0][token]), 10)
        else:
            w *= math.log(docid, 10)
    if wscheme[1] == "p":
        if index[0].get(token) is not None:
            w *= math.log((docid - len(index[0][token])) / len(index[0][token]), 10)
        else:
            w *= math.log(docid - 1, 10)
    memory[1][token] = []
    memory[1][token].append(w)
    return w, memory

def weighTerm(token, index, data, wscheme, c, memory):
    if wscheme == "tfidx":
        wscheme = "tfx"
    if memory[1].get(token) is not None and len(memory[1][token]) == 2:
        return memory[1][token][1], memory
    w, memory = weighTermTop(token, index, data, wscheme, c, memory)
    if wscheme[2] == "c" and index[0].get(token) is not None:
        cosine = 0.0
        for othertoken in c:
            termweight, memory = weighTermTop(othertoken, index, c[othertoken], wscheme, c, memory)
            cosine += termweight * termweight
        w /= math.sqrt(cosine)
    memory[1][token].append(w)
    return w, memory

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
        if index[0].get(token) is None:
            continue
        for i in range(0, len(index[0][token])):
            doc = index[0][token][i][0]
            docs.add(doc)
    for doc in docs:
        for token in index[1][doc]:
            weight, index[2][doc] = weighTerm(token, index, index[1][doc][token], docw, index[1][doc], index[2][doc])
    query = [0, {}]
    queryFreq = {}
    for token in set(tokens):
        count = tokens.count(token)
        queryFreq[token] = count
        if count > query[0]:
            query[0] = count
    for token in set(tokens):
        weight, query = weighTerm(token, index, tokens.count(token), queryw, queryFreq, query)
    cosinequery = 0.0
    for token in query[1]:
        cosinequery += query[1][token][1] * query[1][token][1]
    cosinequery = math.sqrt(cosinequery)
    rank = []
    for doc in docs:
        weight = 0.0
        for token in set(tokens):
            if index[2][doc][1].get(token) is None:
                continue
            weight += query[1][token][1] * index[2][doc][1][token][1]
        cosinedoc = 0.0
        for token in index[2][doc][1]:
            cosinedoc += index[2][doc][1][token][1] * index[2][doc][1][token][1]
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
    index = [{},{},{}]
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