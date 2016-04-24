#!/bin/sh

#This is our comprehensive script for the deliverables 2 - it runs our system end to end.

#Step 1 - preprocess the files

mono preprocess.exe

#Step 2 - make summaries


#Step 3 - Evaluate the summaries using ROUGE

./run_rouge.sh