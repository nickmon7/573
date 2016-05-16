#!/bin/sh

#This is our comprehensive script for the deliverables 3 - it runs our system end to end.

#Step 1 - extract text and preprocess
#uncomment these commands to recache the data
#mono extract.exe
#python preprocess.py

#Step 2 - make summaries

python src/content_selection.py

#Step 3 - Evaluate the summaries using ROUGE

src/run_rouge.sh
