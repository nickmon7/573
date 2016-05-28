import json
import os
import re

from xml.dom.minidom import parse
import xml.dom.minidom

def main():
	sets = r'/dropbox/15-16/573/Data/Documents/devtest/GuidedSumm10_test_topics.xml'
	# create directory for output
	if not os.path.exists('text'):
		os.makedirs('text')

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
		with open('text/' + topic['id'] + '.json', 'w') as outfile:
			json.dump(topic, outfile, indent=4)

def get_doc(id_str):
	# id formats:
	# APW19990421.0284
	# XIN_ENG_20041019.0235

	# possible paths:
	# /LDC02T31/apw/1998/19980601_APW_ENG
	# /LDC08T25/data/apw_eng/apw_eng_200410.xml

	# initialize doc
	doc = {}
	doc['id'] = id_str
	doc['headline'] = ''
	doc['text'] = ''

	# get publication source and year from id
	source = re.search(r'^\w{3}', id_str).group()
	s_year = re.search(r'\d{4}', id_str).group()
	year = int(s_year)

	path = '/corpora/LDC'

	if year <= 2000:
		date = re.search(r'\d{8}', id_str).group()
		path += '/LDC02T31/' + source.lower() + '/' + s_year + '/' + date

		if source == 'APW':
			path += '_APW_ENG'
		elif source == 'NYT':
			path += '_NYT'
		elif source == 'XIE':
			path += '_XIN_ENG'
	else:
		path += '/LDC08T25/data'
		
		name = source.lower() + '_' + 'eng'
		date = re.search(r'\d{6}', id_str).group()
		path += '/' + name + '/' + name + '_' + date + '.xml'

	read_file(doc, path)
	return doc

def read_file(doc, path):
	f = open(path, 'r')
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
			#text = re.sub(r'</?\w+>', ' ', text)
			#text = re.sub(r'\s+', ' ', text)
			#doc['text'] = text.strip()
			break
		else:
			index += 1


main()


