#SCOTT BOMMARITO
#uniqname: zucchini
#ASSIGNMENT 2 (adapted from 1)
#EECS 498 WN 2015

import re
from porterstemmer import PorterStemmer

stopwords = []
dateMonth = "([jJ]an|[jJ]anuary|[fF]eb|[fF]ebruary|[mM]ar|[mM]arch|[aA]pr|[aA]pril|[mM]ay|[jJ]un|[jJ]une|[jJ]ul|[jJ]uly|[aA]ug|[aA]ugust|[sS]ep|[sS]eptember|[oO]ct|[oO]ctober|[nN]ov|[nN]ovember|[dD]ec|[dD]ecember|1[012]|0?[1-9])"
dateDay = "(0?[1-9]|[1-2][0-9]|3[0-1])"
dateYear = "[0-9]*"
dateReg = "(" + dateMonth + "[- ]" + dateDay + "[- ,]" + dateYear + ")"
numReg = "(([0-9]+[,.]?)*[0-9]+)"

#generates the list of stopwords
def generateStopwords():
    global stopwords
    INFILE = open("stopwords")
    for line in INFILE:
        stopwords.append(line.strip().lower())
    INFILE.close()

#removes SGML tags from a text and replaces them with " "
def removeSGML(text):
    return " ".join(re.split("<.*?>", text))

#returns true if the word does not contain a "." and is at least one char long
def wordIsValid(word):
    return len(word) > 0 and not re.match("[.]$", word)

#returns list of tokens in a SGML-less text
def tokenizeText(text):
    dates = re.findall(dateReg, text)
    text = " ".join(re.split(dateReg, text))
    numbers = re.findall(numReg, text)
    text = " ".join(re.split("[0-9]", text))
    tokens = re.split("[\s,;!?()/]*", text)
    newTokens = []
    for puretoken in tokens:
        token = puretoken.lower()
        if re.match(".*n't$", token):
            newTokens.append("not")
            newTokens.append("".join(re.split("n't$", token)))
        elif re.match("let's$", token):
            newTokens.append("us")
            newTokens.append("let")
        elif re.match("I'm$", token):
            newTokens.append("I")
            newTokens.append("am")
        elif re.match(".*'re$", token):
            newTokens.append("are")
            newTokens.append("".join(re.split("'re$", token)))
        elif re.match(".*'s$", token):
            newTokens.append("is")
            newTokens.append("".join(re.split("'s$", token)))
            newTokens.append("'s")
        elif re.match(".*'ve$", token):
            newTokens.append("have")
            newTokens.append("".join(re.split("'ve$", token)))
        elif re.match(".*'d$", token):
            newTokens.append("did")
            newTokens.append("would")
            newTokens.append("had")
            newTokens.append("".join(re.split("'d$", token)))
        elif re.match(".*'ll$", token):
            newTokens.append("will")
            newTokens.append("".join(re.split("'ll$", token)))
        else:
            newTokens.append(token.strip("."))
    tokens = newTokens
    tokens = filter(wordIsValid, tokens)
    for date in dates:
        tokens.append(date[0])
    for number in numbers:
        tokens.append(number[0])
    return tokens

#computes first - second
def listDiff(first, second):
    second = set(second)
    return [x for x in first if x not in second]

#removes stopwords from list of tokens
def removeStopwords(tokens):
    return listDiff(tokens, stopwords)

#stems a single word
def stemWord(str):
    stemmer = PorterStemmer()
    return stemmer.stem(str, 0, len(str)-1)

#stems a list of tokens
def stemWords(tokens):
    return [stemWord(token) for token in tokens]

#processes and tokenizes a file
def processText(text):
    text = removeSGML(text)
    tokens = tokenizeText(text)
    tokens = removeStopwords(tokens)
    return stemWords(tokens)