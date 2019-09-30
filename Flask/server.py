from flask import Flask,jsonify
from flask import request
from werkzeug import secure_filename
import os
mysp=__import__("my-voice-analysis")


app = Flask(__name__)

@app.route("/test",methods = ['GET'])
def test():
    return "working"

@app.route('/uploadfile',methods=['POST'])
def uploadfile():
    try:
        f = request.files['file']
        filePath = os.path.dirname(os.path.realpath(__file__)) +'/'+secure_filename(f.filename)
        f.save(filePath)
        p = f.filename.split('.')[0]
        c = os.path.dirname(os.path.realpath(__file__)) 
        result = mysp.mysptotal(p,c)
        result["status"] = "sucess"
        return jsonify(result)
    except Exception as e:
        result = {
            "status":"failure",
            "exception":e.message
        }
        return jsonify(e)

if __name__ == '__main__':
    try:
        app.run()
    except Exception as e:
        print(e)