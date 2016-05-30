#!/opt/python-3.4/bin/python3.4
import nltk.tree
import os
import re
from subprocess import Popen
from xml.dom.minidom import parse
import xml.dom.minidom

def main():
	summ_dir = '/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/summs'
	parsed_dir = '/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/summ_parsed'

	# for each summary file
	summ_files = []
	for filename in os.listdir(summ_dir):
		path = os.path.join(summ_dir, filename)
		summ_files.append(path)

	# print input list for corenlp
	with open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/summ_list.txt', 'w') as f:
		for name in summ_files:
			f.write(name + '\n')

	# parse summaries
	p = Popen('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/realization/summ_parse.sh', shell=True)
	p.wait()

	# initialize dictionary
	get_model()

	# process each summary
	for filename in os.listdir(summ_dir):
		parsed_path = os.path.join(parsed_dir, filename + '.xml')
		parsed_path += '.xml'
		process_summ(summ_dir, parsed_dir, filename)

def get_model():
	global feat_weights
	curr_class = ''
	# read model file
	model_dir = '/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/realization/training/model.txt'
	lines = []
	with open(model_dir, 'r') as f:
		lines = f.readlines()
	# get feature weights
	for line in lines:
		matches = re.findall(r'\S+', line)
		if len(matches) < 2:
			continue
		first = matches[0]
		if first == 'FEATURES':
			curr_class = matches[3]
			feat_weights[curr_class] = {}
			continue
		prob = float(matches[1])
		feat_weights[curr_class][first] = prob

def process_summ(summ_dir, parsed_dir, filename):
	# parse summary sentences
	parsed_path = os.path.join(parsed_dir, filename + '.xml')
	trees = get_trees(parsed_path)
	output_summ = ''
	for tree in trees:
		trimmed = process_tree(tree)
		output_summ += trimmed + ' '

	# fix output formatting
	output_summ = re.sub("-LRB-", "(", output_summ)
	output_summ = re.sub("-RRB-", ")", output_summ)
	output_summ = re.sub(r"\$\s", "$", output_summ)
	output_summ = re.sub(r"``\s", r"``", output_summ)
	output_summ = re.sub(r"\s''", r"''", output_summ)
	output_summ = re.sub(r"\sn't", r"n't", output_summ)
	output_summ = re.sub(r"\s(?=[.!?,':;%])", "", output_summ)
	output_summ = re.sub(r"\s+", " ", output_summ)

	# overwrite original
	summ_path = os.path.join(summ_dir, filename)
	with open(summ_path, 'w') as f:
		f.write(output_summ)

def get_trees(path):
	DOMTree = xml.dom.minidom.parse(path)
	collection = DOMTree.documentElement
	sentences = collection.getElementsByTagName('sentence')

	trees = []	
	for sent in sentences:
		parse = sent.getElementsByTagName('parse')[0]
		tree_str = parse.firstChild.data
		tree = nltk.ParentedTree.fromstring(tree_str)
		trees.append(tree)
	return trees

def process_tree(tree):
	subtrees = tree.subtrees()
	# get labels of each subtree
	labels = {}
	for st in subtrees:
		label_node(st, labels)
	# get trimmed sentence
	with open('temp', 'w') as f:
		get_trimmed(tree, labels, f)
	trimmed = ''
	with open('temp', 'r') as f:
		trimmed = f.read()
	return trimmed
	
def get_trimmed(node, labels, f):
	label = labels[node.treeposition()]
	if label == 'keep':
		leaves = node.leaves()
		for leaf in leaves:
			f.write(leaf + ' ')
	elif label == 'part':
		for child in node:
			if type(child) == nltk.tree.ParentedTree:
				get_trimmed(child, labels, f)

def label_node(node, labels):
	features = []
	# pos
	features.append('pos=' + node.label())
	leaves = node.leaves()
	if len(leaves) == 1:
		# word
		features.append('word=' + leaves[0].lower())
	elif len(leaves) > 1:
		# first/last leaf pos
		features.append('0_leaf=' + leaves[0].lower())
		features.append('-1_leaf=' + leaves[-1].lower())
		if len(leaves) > 2:
			features.append('1_leaf=' + leaves[1].lower())
			features.append('-2_leaf=' + leaves[-2].lower())
	parent = node.parent()
	if parent != None:
		if parent[0] == node:
			# left-most child
			features.append('LM_child')
		elif len(parent) > 1 and parent[1] == node:
			# second left-most child
			features.append('SLM_child')
		# parent pos
		features.append('p_pos=' + parent.label())
		grandparent = parent.parent()
		if grandparent != None:
			# grandparent pos
			features.append('gp_pos=' + grandparent.label())
	L_sib = node.left_sibling()
	if L_sib != None:
		features.append('L_sib_pos=' + L_sib.label())
	R_sib = node.right_sibling()
	if R_sib != None:
		features.append('R_sib_pos=' + R_sib.label())
	global negatives
	for leaf in leaves:
		if leaf in negatives:
			features.append('negative')
			break

	# fix colons and hashtags
	for i in range(len(features)):
		features[i] = re.sub(r':(?=\S*:)', 'COLON', features[i])
		features[i] = features[i].replace('#', 'HASH')
	# get best label
	label = best_label(features)
	labels[node.treeposition()] = label
	
def best_label(features):
	global feat_weights
	numerators = {}
	for key in feat_weights:
		weights = feat_weights[key]
		weight_sum = weights['<default>']
		for feat in features:
			add_weight = weights.get(feat, 0)
			weight_sum += add_weight
		numerators[key] = weight_sum
	return max(numerators, key=lambda i: numerators[i])

feat_weights = {}
negatives = set(['not', 'n\'t', 'no', 'nor', 'neither'])
main()

