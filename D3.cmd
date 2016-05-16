Executable = /workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/src/d3.sh
Universe   = vanilla
getenv     = true
output     = src/condorLog/d3.out
error      = src/condorLog/d3.err
Log        = src/condorLog/d3.log
transfer_executable = false
request_memory = 2*1024
notification = never
Queue
