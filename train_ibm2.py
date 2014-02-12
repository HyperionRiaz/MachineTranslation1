from collections import *
import math
import sys

if len(sys.argv) !=6:
	print len(sys.argv)
	print "Please run with 5 arguments, ie: python train-ibm2.py <sourceFile> <targetFile> <transTable> <outputFileTrans> <outputFileDistortion>"
	sys.exit()

source = sys.argv[1]
target = sys.argv[2]
trans = sys.argv[3]
transOut = sys.argv[4]
distOut = sys.argv[5]

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

# == Read the source and target tests ==
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

wordsF = []
wordsE = []
distortion = {}
for sent in sentMap.keys():
	fWords = sent.split(" ")
	for word in fWords:
		wordsF.append(word)
	eWords = sentMap[sent]
	eWords = eWords.split(" ")
	for word in eWords:
		wordsE.append(word)
	#Each sentence has its own distortion model. See pg 89 of textbook
	#I is length of english sent, K length of f sent.
	I = len(eWords)
	K = len(fWords) #[fWords countains NULL]
	for k in xrange(0,K): #For all k
		for i in xrange(0,I):
			key = (k,i,I,K) #Translation prob of foreign input word at position k to an english word at position i... summed over all k for fixed i should equal 1!
			distortion[key] = 1/float(K)

print distortion

countWords = Counter() 
vocabF= list(set(wordsF))
vocabE= list(set(wordsE))
for wordE in vocabE:
	for wordF in vocabF:
		pair = (wordE, wordF)
		#wordFtoWordE[pair] = 1/float(len(vocabF))
		countWords[pair] = 0

#print wordFtoWordE #Equivalent to t(e|f) in algorithm. Probabilities are all uniform for every possible word mapping!
#countWords equivalent to count(e|f) in algorithm.


#Algorithm from sheet
n = 0
llPrev = 999
llData = 0
cutoff = 50
count = 0
#while n < 2 or llPrev < llData:
while n < 2 or count < cutoff:
	count+=1
	n+=1
	if n > 1:
		llPrev = llData

	# === E STEP === 
	llData = 0
	wordF = {} #total_t
	for word in vocabF:
		wordF[word] = 0

	for fWord in vocabF:
		for eWord in vocabE:
			pair = (eWord, fWord)
			countWords[pair] = 0

	#Init count_a and total_a
	countDistortion = {}
	triples = []
	for key in distortion.keys():
		triple = (key[1], key[2], key[3])
		triples.append(triple)
		countDistortion[key] = 0 

	totalDistortion = {}
	for triple in triples:
		totalDistortion[triple] = 0

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
				z[english] += distortion[(k, i, I, K)]*wordFtoWordE[pair] #NEW, line 17 algorithm 2, weight

		for i in xrange(0,I):
			english = eWords[i]
			for k in xrange(0,K):
				foreign = fWords[k]
				pair = (english, foreign)
				pik = distortion[(k, i, I, K)]*float(wordFtoWordE[pair]) #NEW, line 21
				countWords[pair] += float(pik)/float(z[english])
				wordF[foreign] += float(pik)/float(z[english])
				countDistortion[(k, i, I, K)] += float(pik)/float(z[english])
				totalDistortion[(i,I,K)] += float(pik)/float(z[english])
			llData += math.log(z[english])

	# === M STEP ===

	for fWord in vocabF:
		for eWord in vocabE:
			pair = (eWord, fWord)
			wordFtoWordE[pair] = float(countWords[pair])/float(wordF[fWord])

	#NEW, line 35-41 algorithm
	for key in distortion.keys():
		k = key[0]
		i = key[1]
		I = key[2]
		K = key[3]
		distortion[key] = countDistortion[key]/totalDistortion[(i,I,K)]

	print str(n) + "\t" + str(llData)

out = ""
print "*** Word translation Probabilities"
for fWord in vocabF:
	for eWord in vocabE:
		pair = (eWord, fWord)
		if str(wordFtoWordE[pair])!="0.0":
			print fWord + "\t" + eWord + "\t" + str(wordFtoWordE[pair])
			out +=fWord + "\t" + eWord + "\t" + str(wordFtoWordE[pair])+"\n"

f = open(transOut, 'w')
f.write(out)
f.close()

#key = (k,i,I,K) #Translation prob of foreign input word at position k to an english word at position i... summed over all k for fixed i should equal 1!

print
out = ""
print "*** Distortion table "
for key in distortion:
	k = key[0]
	i = key[1]
	I = key[2]
	K = key[3]
	prob = distortion[key]
	print str(K-1) +" "+ str(I) +" "+ str(k) +" "+ str(i) +" "+ str(prob) #Length Source, Length Target, position in source, position in source, prob.			
	out += str(K-1) +" "+ str(I) +" "+ str(k) +" "+ str(i+1) +" "+ str(prob)+"\n" #Have to add one to i because it goes from 1 to length of english. Subtract 1 from K because it goes from 0 (NULL word) to length of K

f = open(distOut, 'w')
f.write(out)
f.close()




print
print
for key in distortion:
	k = key[0]
	i = key[1]
	I = key[2]
	K = key[3]
	prob = distortion[key]
	if K == 4 and I == 3:
		print str(K-1) +" "+ str(I) +" "+ str(k) +" "+ str(i+1) +" "+ str(prob)	



