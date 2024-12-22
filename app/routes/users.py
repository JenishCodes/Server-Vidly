from flask import jsonify, request

from app.models import User, Movie, Watchlist, Watched, recommender


def signup():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400

    existing_user = User.get_user_by_email(email)
    if existing_user:
        return jsonify({"error": "Email already in use"}), 400

    new_user = User(name=name, email=email)
    new_user.hash_password(password)

    new_user.save()

    return (
        jsonify(
            {
                "message": "Signed up successfully",
                "token": new_user.get_token(),
                "error": None,
            }
        ),
        200,
    )


def signin():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.check_password(password):
        return jsonify({"error": "Invalid password"}), 400

    return (
        jsonify(
            {
                "message": "Signed in successfully",
                "token": user.get_token(),
                "error": None,
            }
        ),
        200,
    )


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
