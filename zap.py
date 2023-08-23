import requests
import json
import sys
import time


target_url = sys.argv[1]
apikey = 'plv7ln2583k25eg32fgub3bdp5'
### create a tree ####
tree_headers = {"Content-Type":"application/json"}
tree_url = f'http://localhost:8080/JSON/spider/action/scan/?url={target_url}&apikey={apikey}'
### get scan id ###
tree_response = requests.get(tree_url,headers = tree_headers)
scan_id = tree_response.json()['scan']
time.sleep(10)
### start a scan ###
start_headers = {"Content-Type":"application/json"}
# specify the body
request_body = { 
    "scanPolicyName": "Default Policy",
    "recurse": "True"}
start_url = f'http://localhost:8080/JSON/ascan/action/scan/?url={target_url}&apikey={apikey}'
start_response = requests.get(start_url,headers=start_headers,data=request_body)
time.sleep(10)
### check scan state###
getinfo_url = f'http://localhost:8080/JSON/ascan/view/scans/?zapapiformat=JSON&apikey={apikey}'
while True:
    info_response = requests.get(getinfo_url)
    info_list = info_response.json()["scans"]
    info_dic = info_list[0]
    if info_dic["state"] == "FINISHED":
        break
### name the output file ###
name_list = []
if target_url.startswith("https://"):
    name_list = target_url.strip("https://").split(".")
elif target_url.startswith("http://"):
    name_list = target_url.strip("http://").split(".")
file_name = ""
for i in name_list:
   file_name = file_name+"_"+str(i)
file_name = file_name.lstrip("_")
file_name = "/home/jerry/zap/templates/"+file_name+".txt"
### get scan result ###
getresult_headers = {"Content-Type":"application/json","Accept":"application/json"}
getresult_url = f'http://localhost:8080/JSON/core/view/alerts/?baseurl={target_url}&apikey={apikey}'
final_result = requests.get(getresult_url,headers=getresult_headers)
with open(file_name,"w") as f:
    json.dump(final_result.json()["alerts"],f)
f.close()

