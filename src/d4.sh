#!/bin/sh

#This is our comprehensive script for the deliverables 4 - it runs our system end to end.

#Step 1 - extract text and preprocess
#uncomment these commands to recache the data
#python extract.py
#python preprocess.py

#Step 2 - make summaries

python /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/run_system.py

#Step 3 - Evaluate the summaries using ROUGE

/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/run_rouge.sh