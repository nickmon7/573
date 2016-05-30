from nltk.tokenize import word_tokenize, sent_tokenize
import json
import os
import re

def main():
	print 'Preprocessing...'
	#text_dir = '/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/text2/'
	text_dir = 'text2'
	all_topics = load_all_topics(text_dir)
	if not os.path.exists('topics2'):
		os.makedirs('topics2')
	for item in all_topics:
		if len(all_topics[item]) > 0:
			process_topic(all_topics[item])
	print 'Done'

def load_all_topics(text_dir):
	all_topics = {}
	for root,dirs,files in os.walk(text_dir):
		for curr_file in files:
			get_topic_data(os.path.join(root, curr_file), all_topics)
	return all_topics

def get_topic_data(topic_path, all_topics):
	topic_data = {}
	decoder = json.JSONDecoder()
	try:
		topic_data = decoder.decode(str(file(topic_path).read()))
	except:
		print 'Error parsing file ' + topic_path
	all_topics[topic_path.strip(".json").split("/")[-1]] = topic_data
	return all_topics

def process_topic(topic_data):
	# copy topic info
	out_topic = {}
	out_topic['id'] = topic_data['id']
	out_topic['title'] = topic_data['title']
	# iterate through docs in topic
	docSet = []
	for doc in topic_data['docSet']:
		out_doc = {}
		out_doc['id'] = doc['id']
		out_doc['headline'] = doc['headline']
		# process text
		text = process_text(doc['text'])
		# do sentence segmentation on doc
		out_doc['sentences'] = process_sentences(text)
		# get word counts
		out_doc['wordCounts'] = count_words(text)
		docSet.append(out_doc)
	out_topic['docSet'] = docSet
	# output as JSON
	with open('topics2/' + out_topic['id'] + '.json', 'w') as outfile:
		json.dump(out_topic, outfile, indent=4)

def process_text(text):
	# remove tags
	text = re.sub(r'</?\w+>', ' ', text)
	# clean up whitespace
	text = re.sub(r'\s+', ' ', text)
	text = text.strip()
	return text

def process_sentences(text):
	sentences = sent_tokenize(text)
	if len(sentences) > 0:
		# remove location and news source
		sentences[0] = re.sub(r'^(\S+\s+){1,4}(--|_)\s+', '', sentences[0])
	pruned = []
	for sent in sentences:
		# only keep sentences with more than 3 words
		if len(re.findall(r'\S+', sent)) > 3:
			pruned.append(sent)
	return pruned

def count_words(text):
	word_counts = {}
	#tokens = word_tokenize(text)
	tokens = re.split(r'\s+', text)
	for token in tokens:
		t = token.lower()
		t = t.strip('\'\",.!?()[]`-')
		if len(t) == 0:
			continue
		if t in word_counts:
			word_counts[t] += 1
		else:
			word_counts[t] = 1
	return word_counts
	

main()
