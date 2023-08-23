from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import session
import subprocess
import os 
import time
import json
from threading import Thread

import  requests
import datetime
app = Flask(__name__)
app.secret_key = "zaptestkey"
now = datetime.datetime.now()
time_str = now.strftime("%Y-%m-%d %H:%M:%S")
# Print the string representation of the current time
time_str = time_str.replace("-","_").replace(" ","_").replace(":","_") 
@app.route("/")
def index():
    return render_template("index2.html")


@app.route("/runzap",methods=["POST","GET"])
def runzap():
    address = request.form["address"]
    policy = request.form["category"]
    print(policy)
    name_list = []
    com_method = ""
    if address.startswith("https://"):
        name_list = address.strip("https://").split(".")
        com_method = "https"
    elif address.startswith("http://"):
        name_list = address.strip("http://").split(".")
        com_method = "http"
    file_name = ""
    for i in name_list:
        file_name = file_name+"_"+str(i)
    file_name = file_name.lstrip("_")
    webpage = com_method+"_"+file_name
    file_name = file_name + str("_") + str(time_str)
    session["file_name"] = file_name
    # Run the subprocess in a separate thread
    def run_zap():
        subprocess.run(['python3','zap2.py',address,policy,file_name])
    
    t = Thread(target=run_zap)
    t.start()
   
    time.sleep(15)
    return redirect("/wait?webpage={}".format(webpage))
    
@app.route("/wait",methods=["POST","GET"])
def wait():
    webpage = request.args.get("webpage")
    file_name = ""
    # if webpage.startswith("https_"):
    #     file_name = webpage.lstrip("https_")
    # elif webpage.startswith("http_"):
    #     file_name = webpage.lstrip("http_")
    apikey = "plv7ln2583k25eg32fgub3bdp5"
    view_headers = {"Content-Type":"application/json"}
    domain = ""
    domain_list = []
    domain_list = webpage.split("_")
    domain = domain_list[0]+"://"+domain_list[1]
    for i in domain_list[2:-1]:
        domain = domain+"."+i
    view_url = f'http://localhost:8080/JSON/ascan/view/status/?baseurl={domain}&apikey={apikey}' 
    status = 0
    while status != 100: 
        view_response = requests.get(view_url,headers=view_headers)
        status = int(view_response.json()["status"])
        if status != 100:
            return render_template("wait3.html",status = status)
            continue
        else:
            break
    file_name = session.pop("file_name",None)
    return redirect("/present?file_name={}".format(file_name))
    
@app.route("/present",methods = ["POST","GET"])
def present():
    file_name = request.args.get("file_name")
    file_path= "/home/jerry/zap/file/"+str(file_name)+".txt"
    while True:
        if os.path.exists(file_path):
            time.sleep(3)
            break
        else:
            getinfo_url = f'http://localhost:8080/JSON/spider/view/status/?apikey={apikey}'
            info_response = requests.get(getinfo_url)
            status = info_response.json()["status"]
            return render_template("wait3.html")
            time.sleep(1)
            continue
    result_list = []
    with open(file_path) as f :
        result_list = json.load(f)
    risk_order = {"High": 3, "Medium": 2, "Low": 1, "Informational": 0}
    result_list = sorted(result_list, key=lambda x: risk_order[x["risk"]], reverse=True)
    result_dic = {}
    count = -1
    for dic in result_list:
        row_dic = {}
        row_dic["risk"] = dic["risk"]
        row_dic["url"] = dic["url"]
        row_dic["pluginId"] = dic["pluginId"]
        row_dic["alert"] = dic["alert"]
        row_dic["description"] = dic["description"]
        row_dic["solution"] = dic["solution"]
        if row_dic not in result_dic.values():
            count += 1 
            result_dic[count] = row_dic

    return render_template("result.html",data=result_dic)








app.run(port=5000)
