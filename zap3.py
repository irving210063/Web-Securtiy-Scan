import requests
import json
from flask import session
import sys
import time
import datetime
import urllib.parse
from zapv2 import ZAPv2
target_url = sys.argv[1]
policy = sys.argv[2]
file_name = sys.argv[3]
maxdepth = int(sys.argv[4])
maxduration = int(sys.argv[5])
is_credential = sys.argv[6]
login_url= sys.argv[7]
loginusername = sys.argv[8]
loginpassword = sys.argv[9]
apikey = 'plv7ln2583k25eg32fgub3bdp5'
###create a new session############
session_url = f'http://localhost:8080/JSON/core/action/newSession/?apikey={apikey}&name={file_name}'
new_session_response = requests.get(session_url)

#### set the spider setting ###
def set_include_in_context(context_name):
    exclude_url = 'http://localhost:8090/bodgeit/logout.jsp'
    include_url = 'http://localhost:8090/bodgeit.*'
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
print(is_credential)
if is_credential == "No":  ### None credential , so remain as usual 
    print("run nonecredential")
    depth_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDepth/?apikey={apikey}&Integer={maxdepth}'
    maxdepth_response = requests.get(depth_url)

    duration_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDuration/?apikey={apikey}&Integer={maxduration}'
    max_duration_url = requests.get(duration_url)

    ### create a tree ####
    tree_headers = {"Content-Type":"application/json"}
    tree_url = f'http://localhost:8080/JSON/spider/action/scan/?url={target_url}&apikey={apikey}'
    tree_response = requests.get(tree_url,headers = tree_headers)
else:
    print("run credential")
    context_id = 1
    context_name = 'Default Context'
    zap = ZAPv2(apikey=apikey)
    set_include_in_context(context_name)
    depth_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDepth/?apikey={apikey}&Integer={maxdepth}'
    maxdepth_response = requests.get(depth_url)
    duration_url = f'http://localhost:8080/JSON/spider/action/setOptionMaxDuration/?apikey={apikey}&Integer={maxduration}'
    max_duration_url = requests.get(duration_url)
    set_form_based_auth(login_url)
    #set_logged_in_indicator()
    user_id_response = set_user_auth_config(context_id,loginusername,loginpassword)
    start_spider(user_id_response)
    # Include  target URL in Context
    ##includeincontexturl = f'http://localhost:8080/JSON/context/action/includeInContext/?apikey={apikey}&regex={target_url}' 
    ##includecontextresponse = requests.get(includeincontexturl)
    # Set Authentication method 
    ##setauthmethodurl = f'http://localhost:8080/JSON/authentication/action/setAuthenticationMethod/?apikey={apikey}&contextId={context_id}&authMethodName={authmethod}&authMethodConfigParams={Configpara}'
    #setauthmethodresponse = requests.get(setauthmethodurl)
    # Set logout indicator

    # Create user 


    # Force User mode


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


#saved_session_url = f'http://localhost:8080/JSON/core/action/newSession/?apikey={apikey}&name={file_name}'
#saved_session_response = requests.get(saved_session_url)

