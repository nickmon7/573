#!/bin/sh

python /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/content_selection.py $@
python /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/content_selection2.py $@
python /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/output_for_rl.py