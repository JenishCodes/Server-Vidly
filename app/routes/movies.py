from flask import jsonify, request

from app.models import Movie, trie, recommender, Watchlist


def get_movie(movie_id):
    movie = Movie.get_movie(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    return jsonify({"movie": movie, "error": None}), 200


def get_trending_movie():
    movies = Movie.get_trending_movie()

    if request.user:
        movies = Watchlist.populate_is_in_watchlist(movies, request.user)

    return jsonify({"movies": movies, "error": None}), 200


def search_movie():
    query = request.args.get("query")
    limit = int(request.args.get("limit", 10))

    movies = trie.search_prefix(query, limit)

    return jsonify({"movies": movies, "error": None}), 200


def increment_search_count():
    data = request.get_json()

    query = data.get("query")
    movie_id = str(data.get("movie_id"))

    trie.increment_search_count(query, movie_id)

    return jsonify({"message": "Search count incremented", "error": None}), 200


def get_similar_movies(movie_id):
    movie = Movie.get_movie(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    limit = int(request.args.get("limit", 10))

    similar_movies = recommender.get_similar_movies(movie["data"], limit)

    if request.user:
        similar_movies = Watchlist.populate_is_in_watchlist(
            similar_movies, request.user
        )

    return jsonify({"movies": similar_movies, "error": None}), 200


def search_similar_movies():
    query = request.args.get("query")
    limit = int(request.args.get("limit", 10))

    similar_movies = recommender.get_similar_movies(query, limit)

    return jsonify({"movies": similar_movies, "error": None}), 200
