from flask import Flask,jsonify
from flask import request
from werkzeug import secure_filename
import os
mysp=__import__("my-voice-analysis")
from getResult import *
from functools import wraps
import time, math

app = Flask(__name__)
_token = "asdhfusaudifhosdufvdfigyi"

def deleteIfExists(fileName):
    if(os.path.isfile(fileName)):
        os.remove(fileName)

def response(status, message, data):
    return(jsonify({"status":status,"message":message,"data":data}))


def checkTokens(func):
    @wraps(func)
    def check(*args, **kwargs):
        try:
            token = request.headers['token']
            # applicationId = jsonData['applicationId']

            # if token == _token and applicationId == _applicationId:
            if token == _token:
                return func(*args, **kwargs)
            else:
                return response("failure","unauthorized",{})
            
        except Exception as e:
            return response("failure",str(e),{})
    return check


@app.route("/test",methods = ['GET'])
# @checkTokens
def test():
    return "working"

@app.route('/uploadFileRealTime',methods=['POST'])
# @checkTokens
def uploadfileRealTime():
    try:
        
        f = request.files['file']
        fileName = "realtime"+str(math.floor(time.time()))+'.'+f.filename.split('.')[1]
        filePath = os.path.dirname(os.path.realpath(__file__)) +'/'+fileName
        f.save(filePath)
        fc = os.path.dirname(os.path.realpath(__file__))
        result = getResultRealTime(fileName.split('.')[0],fc)
        deleteIfExists(fileName)
        deleteIfExists(fileName.split('.')[0]+".TextGrid")
        # result["status"] = "sucess"
        return response("success", "Audio Analysed", result)
    except Exception as e:
        deleteIfExists(fileName)
        deleteIfExists(fileName.split('.')[0]+".TextGrid")
        return response("failure", str(e), {})

@app.route('/uploadFileBasic',methods=['POST'])
# @checkTokens
def uploadfileBasic():
    try:
        # import pdb; pdb.set_trace()
        f = request.files['file']
        fileName = "basic"+str(math.floor(time.time()))+'.'+f.filename.split('.')[1]
        filePath = os.path.dirname(os.path.realpath(__file__)) +'/'+fileName
        f.save(filePath)
        # p = f.filename.split('.')[0]
        c = os.path.dirname(os.path.realpath(__file__)) 
        result = getResultBasic(fileName.split('.')[0],c)
        # result["status"] = "sucess"
        deleteIfExists(fileName)
        deleteIfExists(fileName.split('.')[0]+".TextGrid")
        return response("success", "Audio Analysed", result)
    except Exception as e:
        # deleteIfExists(fileName)
        # deleteIfExists(fileName.split('.')[0]+".TextGrid")
        return response("failure", e.message, {})

@app.route('/uploadFileAdvanced',methods=['POST'])
# @checkTokens
def uploadfileAdvanced():
    try:
        f = request.files['file']
        fileName = "advanced"+str(math.floor(time.time()))+'.'+f.filename.split('.')[1]
        filePath = os.path.dirname(os.path.realpath(__file__)) +'/'+fileName
        f.save(filePath)
        # p = f.filename.split('.')[0]
        c = os.path.dirname(os.path.realpath(__file__))
        result = getResultAdvanced(fileName.split('.')[0],c) 
        # result = mysp.mysptotal(fileName.split('.')[0],c)
        deleteIfExists(fileName)
        deleteIfExists(fileName.split('.')[0]+".TextGrid")
        # result["status"] = "sucess"
        return response("success", "Audio Analysed", result)
    except Exception as e:
        deleteIfExists(fileName)
        deleteIfExists(fileName.split('.')[0]+".TextGrid")
        return response("failure", e.message, {})

if __name__ == '__main__':
    try:
        app.run()
    except Exception as e:
        print(e)


# tochange speech recognition file init for google api type