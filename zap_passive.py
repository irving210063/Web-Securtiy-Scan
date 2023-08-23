import requests
import json
import sys
import time
target_url = sys.argv[1]
file_name = sys.argv[2]
maxdepth = int(sys.argv[3])
maxduration = int(sys.argv[4])
apikey = 'plv7ln2583k25eg32fgub3bdp5'
session_url = f'http://localhost:8080/JSON/core/action/newSession/?apikey={apikey}&name={file_name}'
new_session_response = requests.get(session_url)
####set the spider setting ###
depth_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDepth/?apikey={apikey}&Integer={maxdepth}'
maxdepth_response = requests.get(depth_url)

duration_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDuration/?apikey={apikey}&Integer={maxduration}'
max_duration_url = requests.get(duration_url)

#### start a spider scan 
tree_headers = {"Content-Type":"application/json"}
tree_url = f'http://localhost:8080/JSON/spider/action/scan/?url={target_url}&apikey={apikey}'
### get scan id ###
tree_response = requests.get(tree_url,headers = tree_headers)
scan_id = tree_response.json()['scan']
getinfo_url = f'http://localhost:8080/JSON/spider/view/status/?apikey={apikey}'
while True:
    info_response = requests.get(getinfo_url)
    status = info_response.json()["status"]
    if int(status) != 100:
        time.sleep(2)
        continue
    else:
        break
file_name = "/home/jerry/zap/passive/"+file_name+".txt"
getresult_url = f'http://localhost:8080/JSON/core/view/alerts/?baseurl={target_url}&apikey={apikey}'
final_result = requests.get(getresult_url)
with open(file_name,"w") as f:
    json.dump(final_result.json()["alerts"],f)
f.close()
