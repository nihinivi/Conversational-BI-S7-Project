from flask import Flask, request, jsonify
from flask_cors import CORS  # <--- import CORS
from base64 import b64encode
app = Flask(__name__)
CORS(app)  # <--- enable CORS for all routes

@app.route("/api/data", methods=["POST"])
def receive_data():
    query = request.form.get("query")
    print("Received query:", query)

    uploaded_file = request.files.get("file")
    if uploaded_file:
         file = uploaded_file.read()
    else:
        print("No file received.")
     


    return jsonify({
        "status": "success",
        "query": query,
        
        "image_url": "https://placehold.co/600x400"
    })



def getTitleImage(id):
	print(id)
	tempfile="data:image/png;base64,"+b64encode(open("test.png","rb").read()).decode()
	if id=="0":
		return ["",""]
	return ["Black",tempfile]

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
    #fill with the needed data for generation
    data=[1760007518,1760003518,1750907518,1750007518]
    data.sort()	
    return jsonify({
        "history": data,}
    )




if __name__ == "__main__":
    app.run(port=5000, debug=True)
