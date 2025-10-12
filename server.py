
from time import time 
from dotenv import load_dotenv
from log_db import (
    insert,
    getlogs,
    getdata
)
load_dotenv()
import pandas as pd
from promptframework import generate_visualization
from flask import Flask, request, jsonify
from flask_cors import CORS   
app = Flask(__name__)
CORS(app)   
 

@app.route("/api/data", methods=["POST"])
def receive_data():
    query = request.form.get("query")
    print("Received query:", query) 
    uploaded_file = request.files.get("file")
    print(uploaded_file)   
    df=pd.read_csv(uploaded_file)
    col_dtype_dict = df.dtypes.apply(lambda x: x.name).to_dict()
    img="data:image/png;base64,"+ generate_visualization(df, col_dtype_dict, query)
    insert(time(), {"query":query,"image":img},"test")
    return jsonify({
        "status": "success",
        "query": query,
        "image_url": img
    }) 


def getTitleImage(id):
	if id=="0" :
                return ["",""]	
	log= getdata(id)[0]
	if id=="0" :
		return ["",""]
	return [log["query"],log["image"]]

@app.route("/api/log", methods=["POST","GET"])
def fetchjson_data():
    query = request.args.get("id")
    print("Received query:", request.form)
    title,image=getTitleImage(query)
    return jsonify({
        "url": image,
	"title":title
    })
 
@app.route("/api/history", methods=["POST","GET"])
def log_data():   
    return jsonify({
        "history": getlogs(),}
    )

 
if __name__ == "__main__":
    app.run(port=5000, debug=True)

