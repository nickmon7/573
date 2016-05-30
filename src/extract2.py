import gzip
import json
import os
import re

from xml.dom.minidom import parse
import xml.dom.minidom

def main():
	sets = r'/dropbox/15-16/573/Data/Documents/evaltest/GuidedSumm11_test_topics.xml'
	# create directory for output
	if not os.path.exists('text2'):
		os.makedirs('text2')

	# read xml
	DOMTree = xml.dom.minidom.parse(sets)
	collection = DOMTree.documentElement
	topics = collection.getElementsByTagName('topic')

	for t in topics:
		topic = {}
		# get topic ID
		topic['id'] = t.getAttribute('id')
		# get topic title
		title = t.getElementsByTagName('title')[0]
		topic['title'] = title.firstChild.data.strip()
		print topic['title']
		# get docSet
		dset = t.getElementsByTagName('docsetA')[0]
		ds = dset.getElementsByTagName('doc')
		docSet = []
		for d in ds:
			id_str = d.getAttribute('id')
			docSet.append(get_doc(id_str))
		topic['docSet'] = docSet
		# output as json
		with open('text2/' + topic['id'] + '.json', 'w') as outfile:
			json.dump(topic, outfile, indent=4)

def get_doc(id_str):
	# id format:
	# XIN_ENG_20041019.0235

	# path format:
	# /LDC11T07/data/apw_eng/apw_eng_200410.xml

	# initialize doc
	doc = {}
	doc['id'] = id_str
	doc['headline'] = ''
	doc['text'] = ''

	# get publication source and year from id
	source = re.search(r'^\w{3}', id_str).group()
	s_year = re.search(r'\d{4}', id_str).group()
	year = int(s_year)

	path = '/corpora/LDC/LDC11T07/data'
		
	name = source.lower() + '_' + 'eng'
	date = re.search(r'\d{6}', id_str).group()
	path += '/' + name + '/' + name + '_' + date + '.gz'

	read_file(doc, path)
	return doc

def read_file(doc, path):
	f = gzip.open(path, 'r')
	#f = open(path, 'r')
	line = f.readline()
	while line:
		if line.startswith('<DOC') and doc['id'] in line:
			raw = line
			while '</DOC>' not in raw:
				raw += f.readline()
			get_text(doc, raw)
			break
		line = f.readline()
	f.close()
			
def get_text(doc, text):
	_tags = re.finditer(r'(<\w+>|<\/\w+>)', text)

	tags = []
	for t in _tags:
		tag = (t.group(), t.start())
		tags.append(tag)

	index = 0
	while index < len(tags):
		tag = tags[index]

		if tag[0] == '</DOC>':
			break
		if tag[0] == '<HEADLINE>':
			start = tag[1] + len(tag[0])
			headline = text[start : tags[index + 1][1]]
			headline = re.sub(r'\s+', ' ', headline)
			doc['headline'] = headline.strip()
			index += 2
		elif tag[0] == '<TEXT>':
			while tags[index][0] != '</TEXT>':
				index += 1
			start = tag[1] + len(tag[0])
			text = text[start : tags[index][1]]
			doc['text'] = text
			break
		else:
			index += 1


main()


