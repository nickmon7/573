#!/bin/sh
java -cp "/NLP_TOOLS/tool_sets/stanford-corenlp/stanford-corenlp-full-2014-01-04/*" -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -props parse.properties
