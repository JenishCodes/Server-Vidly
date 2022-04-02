# Import Packages
from flask import Flask, request, jsonify, send_from_directory, json

# Import Utils Functions
from utils.functions import *

app = Flask(__name__)  # Initialize App

# Routes
@app.route("/")
def checkServer():
    return jsonify({"success": True, "error": None, "data": "Server running properly"}), 200
    

@app.route("/user/interest", methods=['PATCH'])
def getUserInterest():
    req_data = json.loads(request.data)
        
    res = get_recommendations(req_data['history'])

    return jsonify({"success": True, "error": None, "data": res}), 200


@app.route("/movie", methods=["GET", "PATCH"])
def moviesFunc():
    if request.method == "GET":
        res = get_movies([request.args["id"]], dropRows=['keywords'])[0]

        return jsonify({"success": True, "error": None, "data": res}), 200
    elif request.method == "PATCH":
        req_data = json.loads(request.data)
        
        res = get_movies(req_data['movies'], dropRows=['keywords'])
            
        return jsonify({"success": True, "error": None, "data": res}), 200


@app.route("/suggestions", methods=["GET", "PATCH"])
def suggestions():
    if request.method == "GET":
        res = get_suggestions(request.args["key"], int(request.args["count"]))

        return jsonify({"success": True, "error": None, "data": res}), 200
    elif request.method == "PATCH":
        req_data = json.loads(request.data)
        
        increase_movie_score(req_data["key"], req_data["id"])

        return jsonify({"success": True, "error": None}), 200


@app.route("/recommendations/id")
def idRecommendations():
    movie = get_movies([request.args["movie_id"]])[0]
    
    ids = get_movies_from_keywords(movie["keywords"])

    res = get_movies(ids[1:], dropRows=['keywords'])

    return jsonify({"success": True, "error": None, "data": res}), 200


@app.route("/recommendations/keywords")
def keywordRecommendations():
    ids = get_movies_from_keywords(request.args["words"])

    res = get_movies(ids, dropRows=['keywords'])

    return jsonify({"success": True, "error": None, "data": res}), 200


@app.route("/prefixes/save")
def savePrefixes():
    save_as_json()
    
    return jsonify({"success": True, "error": None, "data": "Prefixes Saved"}), 200
    
    
@app.route("/prefixes/download")
def downloadPrefixes():
    return send_from_directory(
        app.root_path, "data/prefixes.json", as_attachment=True
    )


@app.errorhandler(Exception)
def handleException(err):
    return jsonify({"success": False, "error": str(err)}), err.code if hasattr(err, 'code') else 500


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        app.root_path, "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@app.after_request
def addHeaders(response):
    header = response.headers
    header["Access-Control-Allow-Origin"] = "*"
    header["Access-Control-Allow-Methods"] = "*"
    
    return response


# Main Function
if __name__ == "__main__":    
    app.run(debug=False)  # Start App
