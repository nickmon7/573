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
import sys
from subprocess import call,Popen
import os


def load_all_docs(directory):
    all_topics = {}
    for root,dirs,files, in os.walk(directory):
        for current_file in files:
            get_doc_data(os.path.join(root,current_file),all_topics)
    return all_topics


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

def get_doc_data(topic_path,all_topics):
        doc_data = {}
        decoder = json.JSONDecoder()
        try:
            doc_data = decoder.decode(str(file(topic_path).read()))
        except:
            ""
        all_topics[topic_path.strip(".json").split("/")[-1]] = doc_data
        return all_topics


def compare_frequency(word,brown_frequencies,doc_frequencies):
    if word in doc_frequencies:
        if re.search('[^A-z]',word) != None:
            if (word.lower() in brown_frequencies) & (not word.lower() in stopwords.words('english')):
                try:
                    return math.log(float(doc_frequencies[word]) / float(brown_frequencies[word.lower()]))
            #maybe change to frequencies given document
                except ZeroDivisionError:
                    return math.log(float(doc_frequencies[word]))
            else:
                return math.log(float(doc_frequencies[word]))
    return 0.0    

def topic_frequencies(brown_frequencies,topic):
    topic_frequency = {}
    for i,doc in enumerate(topic['docSet']):
        #order sentences in doc
        topic_frequency[doc['id']] = {}
        for sentence in topic['docSet'][i]['sentences']:
            topic_frequency[doc['id']][sentence] = {}
            for word in word_tokenize(sentence):
                topic_frequency[doc['id']][sentence][word] = compare_frequency(word,brown_frequencies,doc['wordCounts'])
    return topic_frequency

#----------------------------------------------training for model----------------------------------------------
##def extract_for_SVM(frequencies,doc_data,sentences,doc_id,test_mode):
##    best_rouge = 0.0
##    if test_mode == True:
##        lib_data = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data_test','a')
##    else:
##        lib_data = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data','a')
##    all_sentence_combs = {}
####    for i,document in enumerate(doc_data['docSet']):
####        for j,sentence in enumerate(document['sentences']):
####            sentences.append((sentence,document['id'],j,i))
##    x = 0
##    current_summary = None
##    while x < 500:
##      output = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/' + doc_id,'w')
##      all_sentence_combs[str(x)] = {'sentences':{},
##                                      'rouge':0.0}
##      current_sentences = []
##      try:
##        randoms = [random.randint(0,len(sentences)) for i in range(0,5)]
##        for v,rands in enumerate(randoms):
##            if randoms.count(rands) > 1:
##                randoms[v] += 1
##        for rand_num in randoms:
##            all_sentence_combs[str(x)]['sentences'][sentences[rand_num][0]] = {'freq' : sentences[rand_num][1],
##                                                                  'position' : rand_num}
##            current_sentences.append(sentences[rand_num][0])
##        summary = create_summary(current_sentences)
##        output.write("\n".join([t for t in summary]))
##        output.close()
##        Popen('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/run_rouge_test.sh ' + "/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/config_files/" + doc_id + ".config.xml 2> err", shell=True)
##        rouge_file = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/rouge_result.txt')
##        all_sentence_combs[str(x)]['rouge'] = 0.0
##        for k,line in enumerate(rouge_file):
##            if k == 7:
##                line = line.split()
##                all_sentence_combs[str(x)]['rouge'] = float(line[3])
##                current_rouge = float(line[3])
##                if current_rouge > best_rouge:
##                    current_summary = summary
##                    best_rouge = current_rouge
##        rouge_file.close()
##        lib_data.write(str(all_sentence_combs[str(x)]['rouge']) + " ")
##        for t,sent in enumerate(all_sentence_combs[str(x)]['sentences']):
##            lib_data.write(str(t) + ":" + str(all_sentence_combs[str(x)]['sentences'][sent]['freq']) + " " + str(t+5) + ":" + str(float(all_sentence_combs[str(x)]['sentences'][sent]['position'])) + " ")
##        lib_data.write("\n")
##      except IndexError:
##          ""
##      x += 1
##    output = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/' + doc_id,'w')
##    output.write("\n".join([t for t in current_summary]))
##    print str(best_rouge) + " " + doc_id
##    output.close()
##    lib_data.close()
#-----------------------------------------------------------------------------------------------------------    
#--------------------------------------testing-----------------------------------------------
def extract_for_SVM(frequencies,doc_data,sentences,doc_id,test_mode):
    best_rouge = 0.0
    if test_mode == True:
        lib_data = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data_test','w')
    else:
        lib_data = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data','a')
    all_sentence_combs = {}
##    for i,document in enumerate(doc_data['docSet']):
##        for j,sentence in enumerate(document['sentences']):
##            sentences.append((sentence,document['id'],j,i))
    x = 0
    current_summary = None
    while x < 20:
      output = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/output/D3/' + doc_id,'w')
      all_sentence_combs[str(x)] = {'sentences':{},
                                      'rouge':0.0}
      current_sentences = []
      try:
        randoms = [random.randint(0,len(sentences)) for i in range(0,5)]
        for v,rands in enumerate(randoms):
            if randoms.count(rands) > 1:
                randoms[v] += 1
        for rand_num in randoms:
            all_sentence_combs[str(x)]['sentences'][sentences[rand_num][0]] = {'freq' : sentences[rand_num][1],
                                                                  'position' : rand_num}
            current_sentences.append(sentences[rand_num][0])
        summary = create_summary(current_sentences)
##        print reorder_by_theme("\n".join([t for t in summary]),stopwords.words('english'),doc_data)
        output.write("\n".join([t for t in summary]))
        output.close()
        all_sentence_combs[str(x)]['rouge'] = 0.0
        p1 = Popen('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/run_rouge_test.sh ' + "/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/config_files/" + doc_id + ".config.xml", shell=True)
        p1.communicate()
        time.sleep(.5)
        rouge_file = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/rouge_result.txt')
        for k,line in enumerate(rouge_file):
            if k == 7:
                line = line.split()
                all_sentence_combs[str(x)]['rouge'] = float(line[3])
        rouge_file.close()
        lib_data.write(str(all_sentence_combs[str(x)]['rouge']) + " ")
        for t,sent in enumerate(all_sentence_combs[str(x)]['sentences']):
            lib_data.write(str(t) + ":" + str(all_sentence_combs[str(x)]['sentences'][sent]['freq']) + " " + str(t+5) + ":" + str(float(all_sentence_combs[str(x)]['sentences'][sent]['position'])) + " ")
        lib_data.write("\n")
      except IndexError:
          ""
      x += 1
    lib_data.close()
    p2 = Popen('svm-scale -l -1 -u 1 /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data_test > /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data_test.scale',shell=True)
    p2.communicate()
##    while not os.path.getsize('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data_test.scale') > 100:
##        print os.path.getsize('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data_test.scale')
##    call('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/predict.sh')
##    best_rouge = 0.0
##    spot = 0
##    for n,line in enumerate(open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/predicition')):
##        print line
##        line = line.split()
##        try:
##            if (float(line[0]) > best_rouge) & (float(line[0]) < .8):
##                best_rouge = float(line[0])
##                spot = n
##        except IndexError:
##            ""
##    file('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/predicition').close()
##    print spot
##    best_summary = create_summary(all_sentence_combs[str(spot)]['sentences'])
##    output = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/output/D3/' + doc_id,'w')
##    output.write(reorder_by_theme("\n".join([t for t in best_summary]),stopwords.words('english'),doc_data))
##    print str(best_rouge) + " " + doc_id
##    output.close()
    json.dump(all_sentence_combs,open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data_test.json','w'))
    lib_data.close()

#------------------------------------------------------------------------------------------



def main():
    test_mode = True
    working_dir = '/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/topics/'
    frequencies = json.load(open(working_dir[:-7] + 'brown_freqs','r'))
    all_docs = load_all_docs(working_dir)
    counter = 0
    for u,item in enumerate(all_docs):
      if str(u) == sys.argv[1]:
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
            extract_for_SVM(frequencies,all_docs,sorted(sentence_probs.items(),reverse=True,key=sentence_probs.get)[0:15],str(item[:-1]) + '-A.M.100.' + str(item[-1]) + ".1",test_mode)
            #----------------------------------------------------------------------------------
##            output.write("\n".join([t[0] for t in ordered_sentences]))
        else:
            output = open(str(item[:-1]) + '-A.M.100.' + str(item[-1]) + ".1",'w')
            output.write(" ")
        break
    if test_mode == False:
        Popen('svm-scale -l -1 -u 1 /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data > /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data.scale',shell=True)
        Popen("svm-train -s 4 -t 1 /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data.scale /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data.model",shell=True)

if __name__== '__main__':
    main()
