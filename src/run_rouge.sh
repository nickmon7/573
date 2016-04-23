#!/bin/sh

#This script runs ROUGE for all four settings four our summaries

CONFIGFILE="/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/configFile.xml"

-e /dropbox/15-16/573/code/ROUGE/data -a -n 1 -x -m -c 95 -r 1000 -f A -p 0.5 -t 0 -l 100 -s -d $CONFIGFILE