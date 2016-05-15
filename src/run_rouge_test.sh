#!/bin/sh

#This script runs ROUGE for all four settings four our summaries

CONFIGFILE="/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/mattRougeTest.xml"

perl /dropbox/15-16/573/code/ROUGE/ROUGE-1.5.5.pl -e /dropbox/15-16/573/code/ROUGE/data -a -n 4 -x -m -c 95 -r 1000 -f A -p 0.5 -t 0 -l 100 -s -d $CONFIGFILE > ../test_for_rouge/D3/rouge_result.txt
