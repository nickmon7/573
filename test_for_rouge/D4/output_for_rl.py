
rl_input = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/rl_input','a')
prediction = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/prediction')
actual_rouge = open('/workspace/ling573_sp_2016/nickmon_calderma_kwlabuda/test_for_rouge/D3/lib_data_test')

actual_rouge2 = actual_rouge.readlines()
for i,line in enumerate(prediction):
    rl_input.write(str(line.strip("\n")) + " " + str(actual_rouge2[i].split()[0]) + "\n")

rl_input.close()
prediction.close()
actual_rouge.close()
