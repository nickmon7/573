#!/bin/sh
java -cp "/NLP_TOOLS/tool_sets/stanford-corenlp/stanford-corenlp-full-2014-01-04/*" -Xmx1g edu.stanford.nlp.pipeline.StanfordCoreNLP -props summ.properties
