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

def main():
    all_sentence_combs = json.load(file(sys.argv[1]))
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
    output = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/output/D3/' + doc_id,'w')
    output.write(reorder_by_theme("\n".join([t for t in best_summary]),stopwords.words('english'),doc_data))
    print str(best_rouge) + " " + doc_id
    output.close()

main()
