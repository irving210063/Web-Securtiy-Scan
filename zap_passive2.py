import requests
import json
import sys
from flask import session
import time
import urllib.parse
import datetime
from zapv2 import ZAPv2
target_url = sys.argv[1]
file_name = sys.argv[2]
print("----zap passive2.py----")
print(file_name)
maxdepth = int(sys.argv[3])
maxduration = int(sys.argv[4])
is_credential = sys.argv[5]
login_url = sys.argv[6]
loginusername = sys.argv[7]
loginpassword = sys.argv[8]
apikey = 'plv7ln2583k25eg32fgub3bdp5'
session_url = f'http://localhost:8080/JSON/core/action/newSession/?apikey={apikey}&name={file_name}'
new_session_response = requests.get(session_url)
def set_include_in_context(context_name,target_url):
    exclude_url = 'http://localhost:8090/bodgeit/logout.jsp'
    include_url = target_url+".*"
    zap.context.include_in_context(context_name, include_url)
    zap.context.exclude_from_context(context_name, exclude_url)
    print('Configured include and exclude regex(s) in context')
def set_logged_in_indicator():
    logged_in_regex = '\Q<a href="logout.jsp">Logout</a>\E'
    zap.authentication.set_logged_in_indicator(context_id, logged_in_regex)
    print('Configured logged in indicator regex: ')
def set_form_based_auth(login_url):
    #login_url = 'http://localhost:8090/bodgeit/login.jsp'
    login_request_data = 'username={%username%}&password={%password%}'
    form_based_config = 'loginUrl=' + urllib.parse.quote(login_url) + '&loginRequestData=' + urllib.parse.quote(login_request_data)
    zap.authentication.set_authentication_method(context_id, 'formBasedAuthentication', form_based_config)
    print('Configured form based authentication')
    
def set_user_auth_config(context_id,username,password):
    user = 'Test User'
    #username = 'test@example.com'
    #password = 'weakPassword'

    user_id = zap.users.new_user(context_id, user)
    user_auth_config = 'username=' + urllib.parse.quote(username) + '&password=' + urllib.parse.quote(password)
    zap.users.set_authentication_credentials(context_id, user_id, user_auth_config)
    zap.users.set_user_enabled(context_id, user_id, 'true')
    zap.forcedUser.set_forced_user(context_id, user_id)
    zap.forcedUser.set_forced_user_mode_enabled('true')
    print('User Auth Configured')
    return user_id
def start_spider(user_id):
    zap.spider.scan_as_user(context_id, user_id, target_url, recurse='false')
    print('Started Scanning with Authentication')
####set the spider setting ###
if is_credential == "No":  ### None credential , so remain as usual 
    print("run nonecredential")
    depth_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDepth/?apikey={apikey}&Integer={maxdepth}'
    maxdepth_response = requests.get(depth_url)
    duration_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDuration/?apikey={apikey}&Integer={maxduration}'
    max_duration_url = requests.get(duration_url)
    ### create a tree ####
    tree_url = f'http://localhost:8080/JSON/spider/action/scan/?url={target_url}&apikey={apikey}'
    tree_response = requests.get(tree_url)
else:
    print("run credential")
    context_id = 1
    context_name = 'Default Context'
    zap = ZAPv2(apikey=apikey)
    set_include_in_context(context_name,target_url)
    depth_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDepth/?apikey={apikey}&Integer={maxdepth}'
    maxdepth_response = requests.get(depth_url)
    duration_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDuration/?apikey={apikey}&Integer={maxduration}'
    max_duration_url = requests.get(duration_url)
    set_form_based_auth(login_url)
    #set_logged_in_indicator()
    user_id_response = set_user_auth_config(context_id,loginusername,loginpassword)
    start_spider(user_id_response)

time.sleep(5)
#scan_id = tree_response.json()['scan']
getinfo_url = f'http://localhost:8080/JSON/spider/view/status/?apikey={apikey}'
while True:
    info_response = requests.get(getinfo_url)
    status = info_response.json()["status"]
    if int(status) != 100:
        time.sleep(2)
        continue
    else:
        break
file_path = "/home/jerry/zap/passive/"+str(file_name)+".txt"
print("----file path---")
print(file_path)
getresult_url = f'http://localhost:8080/JSON/core/view/alerts/?baseurl={target_url}&apikey={apikey}'
final_result = requests.get(getresult_url)
with open(file_path,"w") as f:
    json.dump(final_result.json()["alerts"],f)

