#!/opt/python-3.4/bin/python3.4
import os
import re
from nltk.tree import *

from xml.dom.minidom import parse
import xml.dom.minidom

def main():
	print('Getting training data...')
	# input directories
	parsed_dir = 'orig_parsed'
	comp_dir = 'comp_raw'

	for filename in os.listdir(parsed_dir):
		parsed_path = os.path.join(parsed_dir, filename)
		comp_path = re.sub(r'\.xml', '', filename)
		comp_path = os.path.join(comp_dir, comp_path)
		process_pair(parsed_path, comp_path)

def process_pair(parsed_path, comp_path):
	# get tree from original sentence
	tree = get_tree(parsed_path)
	# get tokens from compressed sentence
	f = open(comp_path, 'r')
	comp_str = f.read()
	f.close()

	comp_str = re.sub(r'\s+', ' ', comp_str)
	# get subtrees by length
	subtrees = list(tree.subtrees())
	subtrees.sort(key = lambda n: len(n.leaves()), reverse=True)
	# find which nodes are kept	
	kept_nodes = {}
	for st in subtrees:
		substring = ' '.join(st.leaves())
		if substring in comp_str:
			comp_str = re.sub(r'\s?' + substring + r'\s?', '', comp_str)			
			kept_nodes[st.treeposition()] = substring
	# assign which nodes are kept
	check_keep_node(kept_nodes, tree, False)
	# assign partial and omitted nodes
	assign_node_status(tree)
	# get features and output them
	global vec_file
	get_features(vec_file, tree)

def get_tree(parsed_path):
	DOMTree = xml.dom.minidom.parse(parsed_path)
	collection = DOMTree.documentElement
	sent = collection.getElementsByTagName('sentence')[0]
	
	parse = sent.getElementsByTagName('parse')[0]
	tree_str = parse.firstChild.data
	tree = ParentedTree.fromstring(tree_str)
	return tree

def check_keep_node(kept_nodes, node, keep):
	if keep:
		node.set_label('K_' + node.label())
	elif len(node.leaves()) == 1:
		node.set_label('O_' + node.label())
	for child in node:
		if type(child) == ParentedTree:
			if keep or child.treeposition() in kept_nodes:
				check_keep_node(kept_nodes, child, True)
			else:
				check_keep_node(kept_nodes, child, False)

def assign_node_status(node):
	# get status of all children
	statuses = []
	for child in node:
		status = get_node_status(child.label())
		if not status:
			assign_node_status(child)
			status = child.label()[0]
		statuses.append(status)
	# assign status
	if 'P' in statuses:			# any children are partial
		node.set_label('P_' + node.label())
	elif 'O' not in statuses:	# all children are kept
		node.set_label('K_' + node.label())
	elif 'K' in statuses:		# some kept, some omitted
		node.set_label('P_' + node.label())
	else:						# all children omitted
		node.set_label('O_' + node.label())

def get_node_status(label):
	if len(label) > 2 and label[1] == '_':
		return label[0]
	return ''

def get_features(f, node):
	# write label
	label = node.label()
	if label[0] == 'K':
		f.write('keep')
	elif label[0] == 'O':
		f.write('omit')
	else:
		f.write('part')
	# pos
	f.write(' pos=' + label[2:] + ':1')
	leaves = node.leaves()
	if len(leaves) == 1:
		# word
		f.write(' word=' + leaves[0].lower() + ':1')
	elif len(leaves) > 1:
		# first/last leaf pos
		f.write(' 0_leaf=' + leaves[0].lower() + ':1')
		f.write(' -1_leaf=' + leaves[-1].lower() + ':1')
		if len(leaves) > 2:
			f.write(' 1_leaf=' + leaves[1].lower() + ':1')
			f.write(' -2_leaf=' + leaves[-2].lower() + ':1')
	parent = node.parent()
	if parent != None:
		if parent[0] == node:
			# left-most child
			f.write(' LM_child:1')
		elif len(parent) > 1 and parent[1] == node:
			# second left-most child
			f.write(' SLM_child:1')
		# parent pos
		f.write(' p_pos=' + parent.label()[2:] + ':1')
		grandparent = parent.parent()
		if grandparent != None:
			# grandparent pos
			f.write(' gp_pos=' + grandparent.label()[2:] + ':1')
	L_sib = node.left_sibling()
	if L_sib != None:
		# left sibling pos
		f.write(' L_sib_pos=' + L_sib.label()[2:] + ':1')
	R_sib = node.right_sibling()
	if R_sib != None:
		# right sibling pos
		f.write(' R_sib_pos=' + R_sib.label()[2:] + ':1')
	global negatives
	for leaf in leaves:
		if leaf in negatives:
			f.write(' negative:1')
			break

	f.write('\n')
	# recurse
	for child in node:
		if type(child) == ParentedTree:
			get_features(f, child)

def fix_output():
	print('Fixing symbols...')
	file_str = ''
	with open('train_vectors.txt', 'r') as f:
		file_str = f.read()
	file_str = re.sub(r':(?=\S*:)', 'COLON', file_str)
	file_str = file_str.replace('#', 'HASH')
	with open('train_vectors.txt', 'w') as f:
		f.write(file_str)
	print('Done')


negatives = set(['not', 'n\'t', 'no', 'nor', 'neither'])
vec_file = open('train_vectors.txt', 'w')
main()
vec_file.close()
fix_output()

