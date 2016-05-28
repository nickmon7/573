import os
import re

def main():
	print 'Extracting sentences...'
	# create output directories
	corpus_dir = 'comp_corpus'
	orig_dir = 'orig_raw'
	comp_dir = 'comp_raw'
	if not os.path.exists(orig_dir):
		os.makedirs(orig_dir)
	if not os.path.exists(comp_dir):
		os.makedirs(comp_dir)

	orig_files = []

	# for each file in the corpus
	for filename in os.listdir(corpus_dir):
		path = os.path.join(corpus_dir, filename)
		with open(path, 'r') as f:
			text = f.read()
			# original
			orig_m = re.findall(r'<original.+original>', text)
			for s in orig_m:
				trimmed = re.sub(r'<\/?original[^>]*>', '', s)
				id_str = re.search(r'id=.+?>', s).group()
				id_str = id_str[3:-1]
				# output raw text to file
				path = os.path.join(orig_dir, id_str)				
				with open(path, 'w') as f:
					f.write(trimmed)
				orig_files.append(path)				
			# compressed
			comp_m = re.findall(r'<compressed.+compressed>', text)
			for s in comp_m:
				trimmed = re.sub(r'<\/?compressed[^>]*>', '', s)
				id_str = re.search(r'id=.+?>', s).group()
				id_str = id_str[3:-1]
				# output raw text to file
				path = os.path.join(comp_dir, id_str)
				with open(path, 'w') as f:
					f.write(trimmed)

	# print input list for corenlp
	with open('input_list.txt', 'w') as f:
		for name in orig_files:
			f.write(name + '\n')
	print 'Done'


main()

