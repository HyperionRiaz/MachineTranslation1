from collections import *
import math
import sys

if len(sys.argv) !=5:
    print "Please run with 4 arguments, ie: python apply-ibm1.py <sourceFile> <targetFile> <trantTableFile> <outputFile>"
    sys.exit()

source = sys.argv[1]
target = sys.argv[2]
trans = sys.argv[3]
outFile = sys.argv[4]

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
        for key in keys:
            if key in wordFtoWordE.keys():    #The prob may be zero, hence there's no entry in the TT         
                if float(wordFtoWordE[key])>max:
                    max = float(wordFtoWordE[key])
                    w = key[0]
                    f = key[1]
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

    
