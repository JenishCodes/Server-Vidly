import os
import datetime

from dotenv import load_dotenv


class Config:
    # Load environment variables
    load_dotenv()

    # Application configuration
    FLASK_ENV = os.getenv("FLASK_ENV")
    DEBUG = os.getenv("DEBUG")

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")

    # JWT configuration
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))
    )

    # CORS configuration
    CORS_ORIGIN = os.getenv("CORS_ORIGIN")

    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL")
    REDIS_PENDING_NODE_THRESHOLD = os.getenv("REDIS_PENDING_NODE_THRESHOLD")

    # Kafka configuration
    KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL")
