import jwt
from functools import wraps
from datetime import datetime, timezone

from flask import request, jsonify

from app.config import Config


def generate_token(user_id):
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,
        "exp": now + Config.JWT_ACCESS_TOKEN_EXPIRES,
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")
    return token


def token_required(f, optional=False):
    """Decorator to ensure the request has a valid JWT token."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if token:
            try:
                data = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
                current_user = data["user_id"]
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired!"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token!"}), 401

            request.user = current_user
        else:
            if not optional:
                return jsonify({"error": "Token is missing!"}), 401

            request.user = None

        return f(*args, **kwargs)

    return decorated_function
