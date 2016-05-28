#!/bin/sh
mallet import-svmlight --input train_vectors.txt --output train_vectors
mallet train-classifier --input train_vectors --output-classifier model --trainer MaxEnt
classifier2info --classifier model > model.txt
rm -f train_vectors model
