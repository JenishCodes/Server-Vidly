from threading import Thread

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


# Initialize SQLAlchemy
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object("app.config.Config")

    # Initialize extensions
    from app import models as _

    db.init_app(app)

    # Enable CORS
    CORS(app)

    return app


def load_app_modules(app):
    # Load data into database
    from app.models import load_data

    load_data()

    # Configure Redis
    from app.redis import configure_redis

    configure_redis(app)

    # Configure Mail
    from app.mailer import Mailer
    
    Mailer(app) 

    # Load models
    from app import models

    models.load_recommender()
    models.build_trie()

    # Start Kafka consumer
    # from app.consumer import Consumer

    # consumer = Consumer()
    # start_consumer_ctx = lambda: consumer.start_consumer(app.app_context)

    # Thread(target=start_consumer_ctx, daemon=True).start()

    # Register routes
    from app.routes import main, auth, user, movie

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(user)
    app.register_blueprint(movie)


def greceful_shutdown(_, __):
    # from app.consumer import Consumer

    # Consumer().shutdown()

    print("Shutting down app...")
    exit(0)
