import requests
import json
import sys
import time
target_url = sys.argv[1]
policy = sys.argv[2]
file_name = sys.argv[3]
maxdepth = int(sys.argv[4])
maxduration = int(sys.argv[5])
apikey = 'plv7ln2583k25eg32fgub3bdp5'
###create a new session############
session_url = f'http://localhost:8080/JSON/core/action/newSession/?apikey={apikey}&name={file_name}'
new_session_response = requests.get(session_url)
#### set the spider setting ###
depth_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDepth/?apikey={apikey}&Integer={maxdepth}'
maxdepth_response = requests.get(depth_url)

duration_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDuration/?apikey={apikey}&Integer={maxduration}'
max_duration_url = requests.get(duration_url)

### create a tree ####
tree_headers = {"Content-Type":"application/json"}
tree_url = f'http://localhost:8080/JSON/spider/action/scan/?url={target_url}&apikey={apikey}'
tree_response = requests.get(tree_url,headers = tree_headers)
time.sleep(2)
### check spider done yet ###
spider_url = f'http://localhost:8080/JSON/spider/view/status/?apikey={apikey}'
while True:
    spider_response = requests.get(spider_url)
    spider_status = spider_response.json()["status"]
    if int(spider_status) != 100:
        time.sleep(2)
        continue
    else:
        break
### start a scan ###
start_headers = {"Content-Type":"application/json"}

start_url = f'http://localhost:8080/JSON/ascan/action/scan?url={target_url}&apikey={apikey}&scanPolicyName={policy}'

start_response = requests.get(start_url,headers=start_headers)
print("--------")
print(start_response)
time.sleep(10)
### check scan state###
getinfo_url = f'http://localhost:8080/JSON/ascan/view/scans?zapapiformat=JSON&apikey={apikey}'
while True:
    info_response = requests.get(getinfo_url)
    info_list = info_response.json()["scans"]
    info_dic = info_list[-1]
    if info_dic["state"] == "FINISHED":
        break
### name the output file ###
# name_list = []
# if target_url.startswith("https://"):
#     name_list = target_url.strip("https://").split(".")
# elif target_url.startswith("http://"):
#     name_list = target_url.strip("http://").split(".")
# file_name = ""
# for i in name_list:
#    file_name = file_name+"_"+str(i)
# file_name = file_name.lstrip("_")
file_name = "/home/jerry/zap/file/"+file_name+".txt"
### get scan result ###
getresult_headers = {"Content-Type":"application/json","Accept":"application/json"}
getresult_url = f'http://localhost:8080/JSON/core/view/alerts?baseurl={target_url}&apikey={apikey}'
final_result = requests.get(getresult_url,headers=getresult_headers)
with open(file_name,"w") as f:
    json.dump(final_result.json()["alerts"],f)
f.close()

#saved_session_url = f'http://localhost:8080/JSON/core/action/newSession/?apikey={apikey}&name={file_name}'
#saved_session_response = requests.get(saved_session_url)

