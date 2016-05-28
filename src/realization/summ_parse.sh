#!/bin/sh
java -cp "/NLP_TOOLS/tool_sets/stanford-corenlp/stanford-corenlp-full-2014-01-04/*" -Xmx1g edu.stanford.nlp.pipeline.StanfordCoreNLP -props "/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/realization/summ.properties"
