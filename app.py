from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
import subprocess
import os 
import time
import json
from threading import Thread

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/runzap",methods=["POST","GET"])
def runzap():
    address = request.form["address"]
    name_list = []
   
    if address.startswith("https://"):
        name_list = address.strip("https://").split(".")
        
    elif address.startswith("http://"):
        name_list = address.strip("http://").split(".")
        
    file_name = ""
    for i in name_list:
        file_name = file_name+"_"+str(i)
    file_name = file_name.lstrip("_")
    
    # Run the subprocess in a separate thread
    def run_zap():
        subprocess.run(['python3','zap.py',address])
    
    t = Thread(target=run_zap)
    t.start()
    
    # Return the redirect to the user immediately
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
            return render_template("wait.html")
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
