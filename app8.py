from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask import session
import subprocess
import os
import time
import json
import threading 
from threading import Thread
import openai
import  requests
import datetime
from werkzeug.utils import secure_filename
import shutil 
import difflib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
nltk.download('stopwords')
nltk.download('punkt')
app = Flask(__name__)
app.secret_key = "zaptestkey"
now = datetime.datetime.now()
time_str = now.strftime("%Y-%m-%d %H:%M:%S")
# Print the string representation of the current time
time_str = time_str.replace("-","_").replace(" ","_").replace(":","_")
@app.route("/")
def index():
    return render_template("home2.html")

@app.route("/runzap",methods=["POST","GET"])
def runzap():
    address = request.form["address"]
    session["address"] = address
    maxdepth = request.form["maxdepth"]
    maxduration = request.form["maxduration"]   
    name_list = []
    com_method = ""
    if address.startswith("https://"):
        name = address.lstrip("https://")
        name = name.replace(".","_").replace("/","_")
        for i in name.split("_"):
            name_list.append(i)
        com_method = "https"
    elif address.startswith("http://"):
        name = address.lstrip("http://")
        name = name.replace(".","_").replace("/","_")
        for i in name.split("_"):
            name_list.append(i)
        com_method = "http"
    # start to store upload files 
    def delete_folder(deleted_folder):
        shutil.rmtree(deleted_folder)
    store_folder =  "/home/jerry/zap/uploaded/" + name  
    uploaded_files = request.files.getlist('folder')
    os.makedirs(store_folder, exist_ok=True)   
    for ifile in uploaded_files: 
        if (ifile.filename.endswith(".html") or ifile.filename.endswith(".js")):
            #print(ifile.filename)
            content = ifile.read().decode('utf-8')  # Read the file content as text
            file_name = ifile.filename.replace("/","_")
            file_name = store_folder+"/"+file_name
            with open(file_name,"w") as f:
                f.write(content)   
    session["dirname"] = name
    ### In order to release storage , delete the opload folder and its contents in 1 hour
    threading.Timer(3600, delete_folder, args=[store_folder]).start() 
    # end of storing files
    file_name = ""
    for i in name_list:
        file_name = file_name+"_"+str(i)
    file_name = file_name.lstrip("_")
    webpage = com_method+"_"+file_name
    file_name = file_name + str("_") + str(time_str)
    scantype = request.form["scantype"]
    if scantype == "active":
        policy = request.form["category"]
        print(policy)
  
    
    # Run the subprocess in a separate thread
        def run_zap():
            subprocess.run(['python3','zap2.py',address,policy,file_name,maxdepth,maxduration])
        t = Thread(target=run_zap)
        t.start()

        session["file_name"] = file_name
        time.sleep(10)
        return redirect("/wait?webpage={}".format(webpage))
    else:
        def run_passive():
            subprocess.run(["python3","zap_passive.py",address,file_name,maxdepth,maxduration])
        t = Thread(target=run_passive)
        t.start()
        session["file_name"] = file_name
        return redirect("/wait_passive?webpage={}".format(webpage))
    

   

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
    slashcount = session.pop("slashcount",None)
    domain = session.pop("address",None)
    spider_url = f'http://localhost:8080/JSON/spider/view/status/?apikey={apikey}'
    while True:
        spider_response = requests.get(spider_url)
        spider_status = spider_response.json()["status"]
        if int(spider_status) != 100:
            return render_template("spider_wait.html",spider_status = spider_status)
        else:
            break
    time.sleep(2)

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
@app.route("/wait_passive",methods=["POST","GET"])
def wait_passive():
    webpage = request.args.get("webpage")
    apikey = "plv7ln2583k25eg32fgub3bdp5"
    time.sleep(3)
    getinfo_url = f'http://localhost:8080/JSON/spider/view/status/?apikey={apikey}'
    while True:
        info_response = requests.get(getinfo_url)
        status = info_response.json()["status"]
        if int(status) != 100:
            time.sleep(1)
            return render_template("wait3.html",status=status)
            continue
        else:
            break
    file_name = session.pop("file_name",None)
    file_path = "/home/jerry/zap/passive/"+str(file_name)+".txt"
    time.sleep(2)
    return redirect("/passive_present?file_name={}".format(file_name))
@app.route("/passive_present",methods = ["POST","GET"])
def passive_present():
    file_name = request.args.get("file_name")
    file_path = "/home/jerry/zap/passive/"+str(file_name)+".txt"
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
        row_dic["messageId"] = dic["messageId"]
        if row_dic not in result_dic.values():
            count += 1
            result_dic[count] = row_dic
    
    return render_template("result3.html",data=result_dic)


@app.route("/present",methods = ["POST","GET"])
def present():
    file_name = request.args.get("file_name")
    apikey = "plv7ln2583k25eg32fgub3bdp5"
    file_path= "/home/jerry/zap/file/"+str(file_name)+".txt"
    while True:
        if os.path.exists(file_path):
            time.sleep(3)
            break
        else:
            getinfo_url = f'http://localhost:8080/JSON/spider/view/status/?apikey={apikey}'
            info_response = requests.get(getinfo_url)
            status = info_response.json()["status"]
            return render_template("wait3.html",status = status)
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
        row_dic["messageId"] = dic["messageId"]
        if row_dic not in result_dic.values():
            count += 1
            result_dic[count] = row_dic

    return render_template("result3.html",data=result_dic)


@app.route("/chatgpt" , methods= ["GET","POST"])
def chatgpt():
    prompt = request.args.get("message")
    #prompt = prompt+" and some code examples"
    # this is irving210063's apikey
    #openai.api_key = "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"
    # this is kobe's api-key
    openai.api_key = "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"

    response = openai.Completion.create(
        engine = "text-davinci-003",    # select model
        prompt = "give me "+prompt+" and code examples",     
        max_tokens = 3500,               # response tokens
        temperature = 1,                # diversity related
        top_p = 1,                   # diversity related
        n = 1,                          # num of response
        )
    progress = "not finished"
    while progress != "stop":
        progress = response["choices"][0]["finish_reason"]
        if progress != "stop":
            continue
        else:
            time.sleep(1)
            answer = response["choices"][0]["text"]
            break
    answer = answer.lstrip("\n").lstrip("\n")
    answer_list = []
    for steps in answer.split("\n\n"):
        answer_list.append(steps)
    return render_template("chatgpt_answer.html",answer_list = answer_list)

@app.route("/revised_response", methods = ["GET","POST"])
def revised_response():
    messageId = request.args.get("messageId")
    alert = request.args.get("alert")
    apikey = "plv7ln2583k25eg32fgub3bdp5"
    response_url = f'http://localhost:8080/JSON/core/view/message?apikey={apikey}&id={messageId}'
    message_response = requests.get(response_url)
    #print(response)
    
    responseBody = message_response.json()["message"]["responseBody"]
    print("-----------responseBody--------------")
    print(responseBody)
    ## two content's similarity function
    def compute_similarity(content1, content2):
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        differ = difflib.SequenceMatcher(None, lines1, lines2)
        similarity_score = differ.ratio()
        similarity_score = round((int(similarity_score) * 100),2)
        return similarity_score 
    ## find similarity file ##
    dirname = session.pop("dirname",None)
    session["dirname"] = dirname
    folder_path = "/home/jerry/zap/uploaded/" + dirname
    file_list = os.listdir(folder_path)
    # Open and process each file
    file_dic = {}
    sim_score = {}
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)  # Full path to the file
        with open(file_path, 'r') as f:
        # Perform operations on the file
            content = f.read()
            file_dic[file_name] = content
            sim_score[file_name] = int(compute_similarity(responseBody,content))
    max_key = max(sim_score, key=lambda k: sim_score[k])
    score = sim_score[max_key]
    mostsimcontent = file_dic[max_key]
    print("-------------mostsimcontent------------")
    print(mostsimcontent)
    for c in sim_score.keys():
        print(c,str(sim_score[c]))
    
    # this is kobe's api-key
    openai.api_key = "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"
    message = "how to solve " + alert + "with below HTML code" + "\n" + mostsimcontent + "\n\n" + "please give me the revised code"
    #print(prompt)
    answerresponse = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",    # select model
        messages =[
            {"role":"system","content":"You are now a IT Security Manager"},
            {"role":"user","content":message}
        ],
        max_tokens = 3500,               # response tokens
        temperature = 1,                # diversity related
        top_p = 1,                   # diversity related
        n = 1,                          # num of response
    )
    progress = "Not yet"
    while progress != "stop":
        progress = answerresponse["choices"][0]["finish_reason"]
        if progress != "stop":
            continue
        else:
            time.sleep(1)
            answer = answerresponse["choices"][0]["message"]["content"]
    answer = answer.lstrip("\n").lstrip("\n")
    answer_list = []

    for i in answer.split("\n\n"):
        answer_list.append(i)
    return render_template("revised_response2.html",answer_list = answer_list,score = score,mostsimcontent = mostsimcontent)



@app.route("/chatgpt_chat",methods=["GET","POST"])
def chatgpt_chat():
    message = request.args.get("message")
    # this is irving210063's api-key
    #openai.api_key = "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"
    #this is kobe 's api-key
    openai.api_key = "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"
    message = "give me "+message+" and code examples"
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",    # select model
        messages =[
            {"role":"system","content":"You are now a IT Security Manager"},
            {"role":"user","content":message}
        ],
        max_tokens = 3500,               # response tokens
        temperature = 1,                # diversity related
        top_p = 1,                   # diversity related
        n = 1,                          # num of response
    )
    progress = "Not yet"
    while progress != "stop":
        progress = response["choices"][0]["finish_reason"]
        if progress != "stop":
            continue
        else:
            time.sleep(1)
            answer = response["choices"][0]["message"]["content"]
    answer = answer.lstrip("\n").lstrip("\n")
    answer_list = []
    
    for i in answer.split("\n\n"):
        answer_list.append(i)
    return render_template("chatgpt_answer.html",answer_list = answer_list)
@app.route("/description", methods=["GET","POST"])
def description():
    description = request.args.get("des")
    alert = request.args.get("alert")
    # this is kobe's API-key
    openai.api_key = "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"
    message = "give me steps to slove "+alert+" and some code examples"
    answerresponse = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",    # select model
        messages =[
            {"role":"system","content":"You are now a IT Security Manager"},
            {"role":"user","content":message}
        ],
        max_tokens = 3500,               # response tokens
        temperature = 1,                # diversity related
        top_p = 1,                   # diversity related
        n = 1,                          # num of response
    )
    progress = "Not yet"
    while progress != "stop":
        progress = answerresponse["choices"][0]["finish_reason"]
        if progress != "stop":
            continue
        else:
            time.sleep(1)
            answer = answerresponse["choices"][0]["message"]["content"]
    answer = answer.lstrip("\n").lstrip("\n")
    answer_list = []

    for i in answer.split("\n\n"):
        answer_list.append(i)
    return render_template("description.html",description=description,answer_list=answer_list)




@app.route("/response",methods = ["GET","POST"])
def response():
    messageId = request.args.get("messageId")
    apikey = "plv7ln2583k25eg32fgub3bdp5"
    response_url = f'http://localhost:8080/JSON/core/view/message?apikey={apikey}&id={messageId}'
    message_response = requests.get(response_url)
    #print(response)
    responseBody = message_response.json()["message"]["responseBody"]
    #print(responseBody)
    return render_template("view_response.html",responseBody = responseBody)



app.run(host="0.0.0.0",port=4000)

