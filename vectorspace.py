#SCOTT BOMMARITO
#uniqname: zucchini
#ASSIGNMENT 2
#EECS 498 WN 2015

import preprocess
import math

docid = 1

def indexDocument(text, docw, queryw, index):
    docid += 1
    tokens = preprocess.tokenizeText(text)
    uniquetokens = set(tokens)
    for token in uniquetokens:
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
        w *= math.log(docid / index[token][0])
    if wscheme[1] == "p":
        w *= math.log((docid - index[token][0]) / index[token][0])
    return w

def weighTerm(token, index, data, wscheme):
    if wscheme == "tfidx":
        wscheme = "tfxtfx"
    w = weighTermTop(token, index, data, wscheme)
    if wscheme[2] == "c":
        sum = 0.0
        for i in range(0, index[token][0]):
            sum += weighTermTop(token, index, token[1][i][1], wscheme)
        w /= sum
    return w

def retrieveDocuments(query, index, docw, queryw):
    tokens = preprocess.tokenizeText(query)
    docs = set()
    docstokens = {}
    for token in tokens:
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
        query[token] = weighTerm(token, index, tokens.count(token), queryw)
    #now use inner product to calculate similarity