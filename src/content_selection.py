import json
from nltk.corpus import brown
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import re
import math
import datetime
import json
import pickle
import os



def create_frequencies():
    frequencies = {}
    news_text = brown.words()
    wnl = WordNetLemmatizer()
    fdist = FreqDist(w.lower() for w in news_text)
    for word in news_text:
        word = wnl.lemmatize(word.lower())
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
        if re.search('[^A-z]',word) != None:
            if word.lower() in brown_frequencies:
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

def create_summary(sorted_sentences):
    word_count = 0
    summary_sentences = []
    for sentence in sorted_sentences:
        tokenized_sentence = sentence.split(" ")
        word_count += len(tokenized_sentence)
        if word_count < 100:
            summary_sentences.append(sentence)
    return summary_sentences
    
#This is D1 Information Ordering method - by date of publication
def reorder(summary_sentences,topic_docs):
    final_summary_sentences = []
    for doc in topic_docs:
        for i,sentence in enumerate(topic_docs[doc]):
            if sentence in summary_sentences:
                final_summary_sentences.append((sentence,doc))
    return sorted(final_summary_sentences,key=lambda x : (datetime.date(int(x[1].split(".")[0][-8:-4]),int(x[1].split(".")[0][-4:-2]),int(x[1].split(".")[0][-2:]))))

def main():
    working_dir = '/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/topics/'
    frequencies = create_frequencies()
    all_docs = load_all_docs(working_dir)
    counter = 0
    for item in all_docs:
        if len(all_docs[item]) > 0:
            counter +=1
            x = topic_frequencies(frequencies,all_docs[item])
            output = open("../output/D2/" + str(item[:-1]) + '-A.M.100.' + str(item[-1]) + ".1",'w')
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
                    for item in x[y][g]:
                        x[y][g][item] = x[y][g][item] / 2.0
                    sentence_probs[g] = sentence_probs[g] / count
            chosen_sentences = create_summary(sorted(sentence_probs,reverse=True,key=sentence_probs.get))
            ordered_sentences = reorder(chosen_sentences,x)
            output.write("\n".join([t[0] for t in ordered_sentences]))
        else:
            output = open(str(item[:-1]) + '-A.M.100.' + str(item[-1]) + ".1",'w')
            output.write(" ")
    



if __name__== '__main__':
    main()
