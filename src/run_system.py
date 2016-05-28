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

def create_frequencies():
    frequencies = {}
    news_text = brown.words()
    fdist = FreqDist(w.lower() for w in news_text)
    for word in news_text:
        frequencies[word] = fdist[word]
    return frequencies


def get_doc_data(topic_path,all_topics):
        doc_data = {}
        decoder = json.JSONDecoder()
        try:
            doc_data = decoder.decode(str(file(topic_path).read()))
        except:
            ""
        all_topics[topic_path.strip(".json").split("/")[-1]] = doc_data
        return all_topics

def load_all_docs(directory):
    all_topics = {}
    for root,dirs,files, in os.walk(directory):
        for current_file in files:
            get_doc_data(os.path.join(root,current_file),all_topics)
    return all_topics


def compare_frequency(word,brown_frequencies,doc_frequencies):
    if word in doc_frequencies:
        if re.search('[^A-z]',word) == None:
            if (word in brown_frequencies) & (not word in stopwords.words('english')):
                try:
                    return math.log(float(doc_frequencies[word]) / float(brown_frequencies[word]))
            #maybe change to frequencies given document
                except ZeroDivisionError:
                    return math.log(float(doc_frequencies[word]))
            else:
                return math.log(float(doc_frequencies[word]))
    return 0.0
        
def topic_frequencies(brown_frequencies,topic):
    topic_frequency = {}
    all_words = {}
    for doc in topic['docSet']:
        for word in doc['wordCounts']:
            if word.lower() in all_words:
                all_words[word.lower()] += 1.0
            else:
                all_words[word.lower()] = 1.0
    for i,doc in enumerate(topic['docSet']):
        #order sentences in doc
        topic_frequency[doc['id']] = {}
        for sentence in topic['docSet'][i]['sentences']:
            topic_frequency[doc['id']][sentence] = {}
            for word in word_tokenize(sentence):
                topic_frequency[doc['id']][sentence][word] = compare_frequency(word.lower(),brown_frequencies,all_words)
    return topic_frequency


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
    test_mode = True
    working_dir = '/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/topics/'
    frequencies = json.load(open(working_dir[:-7] + 'brown_freqs','r'))
    all_docs = load_all_docs(working_dir)
    counter = 0
    for u,item in enumerate(all_docs):
        if len(all_docs[item]) > 0:
            counter +=1
            x = topic_frequencies(frequencies,all_docs[item])
            output = open("/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/output/D3/" + str(item[:-1]) + '-A.M.100.' + str(item[-1]) + ".1",'w')
        ##    for y in x:
        ##        print str(y) + "\n\n\n"
            #change to sort by date
            sentence_probs = {}
            for y in x:
                for g in x[y]:
                    count = 0.0
                    for q in x[y][g]:
                        if g in sentence_probs:
                            sentence_probs[g] += float(x[y][g][q])
                            count += 1.0
                        else:
                            sentence_probs[g] = float(x[y][g][q])
                            count += 1.0
                    for e in x[y][g]:
                        x[y][g][e] = x[y][g][e] / 2.0
                    sentence_probs[g] = sentence_probs[g] / count
            #--------------------------add position in document--------------------------------
            p1 = Popen("/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/run_test_scripts.sh " + str(u) + " " + item,shell=True)
            p1.communicate()
            #----------------------------------------------------------------------------------
##            output.write("\n".join([t[0] for t in ordered_sentences]))
        else:
            output = open(str(item[:-1]) + '-A.M.100.' + str(item[-1]) + ".1",'w')
            output.write(" ")
    if test_mode == False:
        Popen('svm-scale -l -1 -u 1 /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data > /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data.scale',shell=True)
        Popen("svm-train -s 4 -t 1 /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data.scale /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data.model",shell=True)

main()
