# Import Packages
import os
from flask import Flask, request, jsonify, send_from_directory

# Import Utils Functions
from utils.functions import *

app = Flask(__name__)  # Initialize App

# Routes
@app.route("/user/interest", methods=['POST'])
def getUserInterest():
    try:
        req_data = request.get_json()
        
        res = get_recommendations(req_data['history'])

        return jsonify({"success": True, "error": None, "data": res}), 200
    except Exception as err:
        print(err)
        return jsonify({"success": False, "error": "Internal Server Error"}), 400


@app.route("/movie")
def getMovie():
    try:
        res = get_movie(request.args["id"])

        return jsonify({"success": True, "error": None, "data": res}), 200
    except Exception as err:
        print(err)
        return jsonify({"success": False, "error": "Internal Server Error"}), 400


@app.route("/movie/suggestions")
def getSuggestions():
    try:
        res = get_suggestions(request.args["key"])

        return jsonify({"success": True, "error": None, "data": res[:30]}), 200
    except Exception as err:
        print(err)
        return jsonify({"success": False, "error": "Internal Server Error"}), 400


@app.route("/movie/score", methods=["POST"])
def increaseMovieScore():
    try:
        increase_movie_score(request.args["key"], request.args["id"])

        return jsonify({"success": True, "error": None}), 200
    except Exception as err:
        print(err)
        return jsonify({"success": False, "error": "Internal Server Error"}), 400


@app.route("/movie/id/recommendations")
def idRecommendations():
    try:
        movie = get_movie(request.args["id"])
        ids = get_movies_from_keywords(movie["keywords"])

        res = get_movies(ids[1:])

        return jsonify({"success": True, "error": None, "data": res}), 200
    except Exception as err:
        print(err)
        return jsonify({"success": False, "error": "Internal Server Error"}), 400


@app.route("/movie/keywords/recommendations")
def keywordRecommendations():
    try:
        ids = get_movies_from_keywords(request.args["words"])

        res = get_movies(ids)

        return jsonify({"success": True, "error": None, "data": res}), 200
    except Exception as err:
        print(err)
        return jsonify({"success": False, "error": "Internal Server Error"}), 400


# Required Extra Routes
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        app.root_path, "data/favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@app.route("/shutdown")
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")

    save_as_json()
    func()
    return "Data Saved."


@app.after_request
def addHeaders(response):
    header = response.headers
    header["Access-Control-Allow-Origin"] = "*"

    return response


# Main Function
if __name__ == "__main__":
    app.run(debug=True)  # Start App
