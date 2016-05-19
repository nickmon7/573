from nltk.corpus import brown, stopwords
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import random
import re
import math
import time
import datetime
import json
from subprocess import call,Popen
import os
import sys

def create_summary(sorted_sentences):
    word_count = 0
    summary_sentences = []
    for sentence in sorted_sentences:
        tokenized_sentence = sentence.split(" ")
        word_count += len(tokenized_sentence)
        if word_count < 100:
            summary_sentences.append(sentence)
    return summary_sentences

#This method reorders a summary by themes...
#1st parameter = summary comes in as a STRING... 
#2nd parameter = stopwords is list of stopwords
#3rd parameter = the token dictionary for the doc set

def reorder_by_theme(summary, stopwords, docSetDict):
	nounTags = [] #This list is how we'll make sure our theme is a noun
	nounTags.append("NN")
	nounTags.append("NNS")
	nounTags.append("NNP")
	nounTags.append("NNPS")
	themeDict = {} 
	"""
	(1) SAVE TUPLE OF (winning theme, sentence, 0)
	(2) look up docset's score for theme,      ^^^^
	(3)Order sentences based on tuple[2] (print tuple[1])
	
	"""
	sentenceThemeList = [] #This is a list of (theme, sentence, score) for each sentence in the summary
	sentences = nltk.sent_tokenize(summary)
	for sentence in sentences:
		for word in nltk.word_tokenize(sentence):
			if word not in stopwords and word.isalnum(): #This gets rid of punctuation
				if word in themeDict:
					themeDict[word]+=1
				else: #word not already in dictionary
					themeDict[word]= 1
		themeList = sorted(themeDict, reverse=True, key=themeDict.get)
		#nltk.pos_tag(list)[0][1] gives us the POS for a given word 
		#(you have to make the word into a list for this to work)
		winningTheme = ""
		#This block ensures we get a NOUN as the winning theme
		if len(themeList)>0: 
			for i in range(0, len(themeList)):
				temp = []
				temp.append(themeList[i])
				taggedWord = nltk.pos_tag(temp)
				if taggedWord[0][1] in nounTags: ##if theme is a noun, it is chosen
					winningTheme = themeList[i]
					tuple = list((winningTheme, sentence, 0)) 
					sentenceThemeList.append(tuple)
					break
		else: #This block executes only if we have an empty summary
			nulltuple = list(('nothing', sentence, 0)) #tuples aren't modifiable
			sentenceThemeList.append(nulltuple)

	#HERE - we loop through the sentences and make their theme scores the docSet's theme scores
	#then reorder based on those scores and return that list
	for i in range (0, len(sentenceThemeList)):
		tup = sentenceThemeList[i]
		theme = tup[0]
		docSetScore = 0
		if theme in docSetDict:
			docSetScore = docSetDict[theme]
		tup[2] = docSetScore	
		print("The score for theme " + str(theme)+ " is "+ str(tup[2]))
		
	sortedByTheme = sorted(sentenceThemeList,reverse=True,key=lambda x : x[2])
	newSummary = ""
	for tuple in sortedByTheme:
		newSummary+=" "+tuple[1] #this concatenates the reordered sentences together
	return newSummary.strip()

def main():
    all_sentence_combs = json.load(file('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data_test.json'))
    best_rouge = 0.0
    spot = 0
    p2 = Popen('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/predict.sh',shell=True)
    p2.communicate()
    for n,line in enumerate(open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/prediction')):
        print line
        line = line.split()
        try:
            if (float(line[0]) > best_rouge) & (float(line[0]) < .8):
                best_rouge = float(line[0])
                spot = n
        except IndexError:
            ""
    file('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/prediction').close()
    print spot
    best_summary = create_summary(all_sentence_combs[str(spot)]['sentences'])
    output = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/output/D3/' + str(sys.argv[2][:-1]) + '-A.M.100.' + str(sys.argv[2][-1]) + ".1",'w')
    output.write(reorder_by_theme("\n".join([t for t in best_summary]),stopwords.words('english'),json.load(file('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/all_docs.json'))))
    print str(best_rouge) + " " + str(sys.argv[2][:-1]) + '-A.M.100.' + str(sys.argv[2][-1]) + ".1"
    output.close()

main()
