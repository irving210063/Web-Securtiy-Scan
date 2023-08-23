from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
import subprocess
import os 
import time
import json
from threading import Thread

import  requests
app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/runzap",methods=["POST","GET"])
def runzap():
    address = request.form["address"]
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
    
    # Run the subprocess in a separate thread
    def run_zap():
        subprocess.run(['python3','zap.py',address])
    
    t = Thread(target=run_zap)
    t.start()
    webpage = com_method+"_"+file_name
    time.sleep(15)
    return redirect("/wait?webpage={}".format(webpage))
    
@app.route("/wait",methods=["POST","GET"])
def wait():
    webpage = request.args.get("webpage")
    file_name = ""
    if webpage.startswith("https_"):
        file_name = webpage.lstrip("https_")
    elif webpage.startswith("http_"):
        file_name = webpage.lstrip("http_")
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
            return render_template("wait2.html",status = status)
            continue
        else:
            break
    return redirect("/present?file_name={}".format(file_name))
    
@app.route("/present",methods = ["POST","GET"])
def present():
    file_name = request.args.get("file_name")
    file_path= "/home/jerry/zap/templates/"+file_name+".txt"
    while True:
        if os.path.exists(file_path):
            time.sleep(3)
            break
        else:
            return render_template("wait2.html")
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
