from collections import *
import math
import sys

if len(sys.argv) !=6:
    print "Please run with 5 arguments, ie: python apply_ibm2.py <sourceFile> <targetFile> <trantTableFile> <distTableFile> <outputFile>"
    sys.exit()

source = sys.argv[1]
target = sys.argv[2]
trans = sys.argv[3]
distFile = sys.argv[4]
outFile = sys.argv[5]

def parseDistortion(filePath):
    f = open(filePath,"r+")
    text = f.read()
    data = text.split("\n")
    dist = {}    
    count = 0
    for sent in data:
        if sent != "":
            entries = sent.split(" ")
            k = float(entries[2]) #Position in f
            i = float(entries[3]) #Position in e
            I = float(entries[1]) #Length of e
            K = float(entries[0]) #Length of f
            prob = entries[4] #Prob a(k|i,I,K)
            #Will store in distortion textfile format, ie K, I, k, i, p . k range from [0,K] and sum over all k = 1 for fixed i, K, I. k = 0 refers to NULL word.
            key = (K,I,k,i)
            dist[key] = float(prob)

    f.close()
    return dist

def parseFile(filePath, source):
    f = open(filePath,"r+")
    text = f.read()
    data = text.split("\n")
    sents = {}    
    count = 0
    for sent in data:
        if sent != "":
            if source:
                sent = "NULL " + sent
            sents[count] = sent
            count=count+1
    f.close()

    return sents

dist = parseDistortion(distFile)
print dist
enFile = target
deFile = source
enHash = parseFile(enFile, False)
deHash = parseFile(deFile, True)
numSents = len(enHash.keys())
pEgivenG = {}
sentMap = {}


for i in xrange(0, numSents):
    sentMap[deHash[i]] = enHash[i]

# == Read translation table from Model 1 ==
wordFtoWordE = {}
with open(trans) as f:
    content = f.readlines()

for wordPair in content:
    words = wordPair.split("\t")
    pair = (words[1], words[0])
    wordFtoWordE[pair] = float(words[2])

# == Carry out alignment ===
output = ""
#for sent in sentMap:
for i in xrange(0, numSents):
    sent = deHash[i]
    wordsF =sent.split(" ")
    eng = sentMap[sent]
    wordsE = eng.split(" ")
    align = ""
    falign = ""

    for wordE in wordsE:
        keys = [(wordE,x) for x in wordsF] #All possible words in the F sentence this word could be paired with
        max = 0 #Find the source word with the max prob of P(wordE | sourceWord)
        w = ""
        finW = ""
        finF = ""
        for key in keys:
            w = key[0]
            f = key[1]
            posF = wordsF.index(f)+1-1  #This number word in F sentence aligns to wordE. Have to add 1 because of list indexes, have to minus 1 because of NULL word! Is poss to get a 0 here => NULL   
            posE = wordsE.index(wordE)+1 #This number word in E sentence aligned to f word. Have to add 1 because of list indexs.
            k = (len(wordsF)-1, len(wordsE), posF, posE)
            distProb = dist[k]
            if key in wordFtoWordE.keys():    #The prob may be zero, hence there's no entry in the TT         
                if float(wordFtoWordE[key])*distProb>max:
                    max = float(wordFtoWordE[key])*distProb
                    finW = w
                    finF = f
        
        w = finW
        f = finF
        posF = wordsF.index(f)+1-1
        posE = wordsE.index(wordE)+1
        k = (len(wordsF)-1, len(wordsE), posF, posE)
        print posF
        print posE
        print dist[k]

        if w == "": #Couldn't find a F word for the E word to align to....all had prob 0....so allign to null? pg 85 textbook.
            align += wordE + "\t"   
            output += str(0) + " "
            falign += "NULL" + "\t"
        elif f == "NULL":
            print "ALINING TO NULL, set OUPUT TO 0"
            align += wordE + "\t"   
            output += str(0) + " "
            falign += "NULL" + "\t"
        else:    
            align += w + "\t"   
            output += str(wordsF.index(f)) + " " 
            falign += f + "\t"
    print align
    print falign
    print
    output +="\n"

f = open(outFile, 'w')
f.write(output)
f.close()

    #python aln2latex.py -s toy.en -t toy.de -f 
'''
    for wordF in wordsF:
        keys = [(x,wordF) for x in wordsE]
        max = 0
        w = ""
        for key in keys:
            if float(wordFtoWordE[key])>max:
                max = float(wordFtoWordE[key])
                w = key[0]
                f = key[1]
        align += w + "\t"   
        falign += f + "\t"
    print align
    print falign
    print
'''

    
