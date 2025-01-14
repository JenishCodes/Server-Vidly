from flask import jsonify, request
import random

from app.models import User
from app.redis import redis_client
from app.mailer import Mailer


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

    return jsonify({"token": new_user.get_token(), "error": None}), 201


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

    return jsonify({"token": user.get_token(), "error": None}), 200


def send_otp():
    data = request.get_json()

    email = data.get("email")

    if not email:
        return jsonify({"error": "email is required"}), 400

    user = User.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = redis_client.get("otp:forgot_password:" + email)
    if otp:
        return jsonify({"error": "OTP already sent"}), 400

    otp = random.randint(100000, 999999)

    subject = "Forgot Password OTP Request"
    body = f"Your OTP is {otp}. It will expire in 5 minutes."

    mailer = Mailer.get_mailer()
    mailer.send_mail([email], subject, body)

    redis_client.set("otp:forgot_password:" + email, otp, ex=5 * 60)

    return jsonify({"message": "OTP sent", "error": None}), 200


def change_password():
    data = request.get_json()

    email = data.get("email")
    otp = data.get("OTP")
    password = data.get("password")

    if not email or not otp or not password:
        return jsonify({"error": "email, otp and password are required"}), 400

    sent_otp = redis_client.get("otp:forgot_password:" + email)
    if not otp:
        return jsonify({"error": "OTP expired"}), 400
    if sent_otp != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    user = User.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.hash_password(password)
    user.save()

    redis_client.delete("otp:forgot_password:" + email)

    return jsonify({"message": "Password updated", "error": None}), 200
