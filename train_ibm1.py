from collections import *
import math
import sys

if len(sys.argv) !=4:
	print "Please run with 3 arguments, ie: python train-ibm1.py <sourceFile> <targetFile> <outputFile>"
	sys.exit()

source = sys.argv[1]
target = sys.argv[2]
output = sys.argv[3]

print source,target,output

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

#print sentMap #Sentence pairs (e,f) - f is the key, e is the value.

wordsF = []
wordsE = []
wordFtoWordE = {}
for sent in sentMap.keys():
	fWords = sent.split(" ")
	for word in fWords:
		wordsF.append(word)
	eWords = sentMap[sent]
	eWords = eWords.split(" ")
	for word in eWords:
		wordsE.append(word)

countWords = Counter() 
vocabF= list(set(wordsF))
vocabE= list(set(wordsE))
for wordE in vocabE:
	for wordF in vocabF:
		pair = (wordE, wordF)
		wordFtoWordE[pair] = 1/float(len(vocabF))
		countWords[pair] = 0

#print wordFtoWordE #Equivalent to t(e|f) in algorithm. Probabilities are all uniform for every possible word mapping!
#countWords equivalent to count(e|f) in algorithm.


#Algorithm from sheet
n = 0
llPrev = 999
llData = 0
count = 0
cutoff = 27
print "Running EM for Model 1 stopping after " + str(cutoff) + " iterations."
#while n < 2 or llPrev < llData:
while n < 2 or count < cutoff:
	count = count +1
	n+=1
	if n > 1:
		llPrev = llData

	# === E STEP === 
	llData = 0
	wordF = {}
	for word in vocabF:
		wordF[word] = 0

	countWords.clear() #Resets all entries to 0!
	
	for sent in sentMap.keys():
		fWords = sent.split(" ")
		trans = sentMap[sent]
		eWords = trans.split(" ")
		I = len(eWords)
		K = len(fWords)
		z = {} #Norm for a word
		for i in xrange(0,I): #Loop over all possible word alignments in two aligned sentences
			english = eWords[i]
			z[english] = 0
			for k in xrange(0,K):
				foreign = fWords[k]
				pair = (english, foreign)
				z[english] += wordFtoWordE[pair]

		for i in xrange(0,I):
			english = eWords[i]
			for k in xrange(0,K):
				foreign = fWords[k]
				pair = (english, foreign)
				countWords[pair] += float(wordFtoWordE[pair])/float(z[english])
				wordF[foreign] += float(wordFtoWordE[pair])/float(z[english])
			llData += math.log(z[english])

	# === M STEP ===

	for fWord in vocabF:
		for eWord in vocabE:
			pair = (eWord, fWord)
			wordFtoWordE[pair] = float(countWords[pair])/float(wordF[fWord])

	print str(n)+"\t" + str(llData)

out = ""
print "*** Word translation Probabilities"
for fWord in vocabF:
	for eWord in vocabE:
		pair = (eWord, fWord)
		if str(wordFtoWordE[pair])!="0.0":
			print fWord + "\t" + eWord + "\t" + str(wordFtoWordE[pair])
			out +=fWord + "\t" + eWord + "\t" + str(wordFtoWordE[pair])+"\n"

f = open(output, 'w')
f.write(out)
f.close()