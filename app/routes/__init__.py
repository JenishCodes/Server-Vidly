import logging
from functools import wraps

from flask import Blueprint

from app.jwt import token_required
from app.routes import users, movies, auths


# Initialize the Blueprint for user-related users
main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__, url_prefix="/auth")
user = Blueprint("user", __name__, url_prefix="/user")
movie = Blueprint("movie", __name__, url_prefix="/movie")


# Error handler for all routes
def handle_exception(controller):
    @wraps(controller)
    def wrapper(*args, **kwargs):
        try:
            return controller(*args, **kwargs)
        except Exception as e:
            logging.error(e)
            return {"error": "Internal server error"}, 500

    return wrapper


# Register each route to the main blueprint
main.add_url_rule("/", view_func=lambda: "Welcome to the Movie API", methods=["GET"])


# Register each route to the auth blueprint
auth.add_url_rule("/signup", view_func=handle_exception(auths.signup), methods=["POST"])
auth.add_url_rule("/signin", view_func=handle_exception(auths.signin), methods=["POST"])
auth.add_url_rule("/otp", view_func=handle_exception(auths.send_otp), methods=["POST"])
auth.add_url_rule("/password", view_func=handle_exception(auths.change_password), methods=["POST"])


# Register each route to the user blueprint
user.add_url_rule(
    "/me", view_func=handle_exception(token_required(users.get_user)), methods=["GET"]
)

user.add_url_rule(
    "/watchlist",
    view_func=handle_exception(token_required(users.get_watchlist)),
    methods=["GET"],
)
user.add_url_rule(
    "/watchlist/<string:movie_id>",
    view_func=handle_exception(token_required(users.update_watchlist)),
    methods=["POST"],
)

user.add_url_rule(
    "/watch/<string:movie_id>",
    view_func=handle_exception(token_required(users.watch)),
    methods=["POST"],
)

user.add_url_rule(
    "/history",
    view_func=handle_exception(token_required(users.get_history)),
    methods=["GET"],
)
user.add_url_rule(
    "/history",
    view_func=handle_exception(token_required(users.clear_history)),
    methods=["PUT"],
)

user.add_url_rule(
    "/recommended",
    view_func=handle_exception(token_required(users.get_recommended_movies)),
    methods=["GET"],
)


# Register each route to the movie blueprint
movie.add_url_rule(
    "/<string:movie_id>", view_func=handle_exception(movies.get_movie), methods=["GET"]
)

movie.add_url_rule(
    "/trending",
    view_func=handle_exception(
        token_required(movies.get_trending_movie, optional=True)
    ),
    methods=["GET"],
)

movie.add_url_rule(
    "/search", view_func=handle_exception(movies.search_movie), methods=["GET"]
)
movie.add_url_rule(
    "/search/increment",
    view_func=handle_exception(movies.increment_search_count),
    methods=["POST"],
)

movie.add_url_rule(
    "/similar/<string:movie_id>",
    view_func=handle_exception(
        token_required(movies.get_similar_movies, optional=True)
    ),
    methods=["GET"],
)
movie.add_url_rule(
    "/similar/search",
    view_func=handle_exception(movies.search_similar_movies),
    methods=["GET"],
)
