from flask import jsonify, request

from app.models import User, Movie, Watchlist, Watched, recommender


def get_user():
    user = User.query.get(request.user)

    return jsonify({"user": user.to_dict(), "error": None}), 200


def get_watchlist():
    movies = Watchlist.get_movie(request.user)

    for movie in movies:
        movie["is_in_watchlist"] = True

    return jsonify({"movies": movies, "error": None}), 200


def update_watchlist(movie_id):
    Watchlist.update_watchlist(request.user, movie_id)

    return jsonify({"message": "Watchlist updated", "error": None}), 200


def watch(movie_id):
    Watched.watch_movie(request.user, movie_id)

    Movie.increase_watch_count(movie_id)

    return jsonify({"message": "Movie watched", "error": None}), 200


def get_history():
    movies = Watched.get_history(request.user)

    return jsonify({"movies": movies, "error": None}), 200


def clear_history():
    Watched.clear_history(request.user)

    return jsonify({"message": "History cleared", "error": None}), 200


def get_recommended_movies():
    history = Watched.get_history(request.user)

    watched = {movie["id"]: movie["data"] for movie in history}
    if not watched:
        return jsonify({"movies": [], "error": None}), 200

    recommended_movies = recommender.get_recommended_movies(watched)

    return jsonify({"movies": recommended_movies, "error": None}), 200
