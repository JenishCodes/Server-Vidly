from datetime import datetime, timezone

from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from .movie import Movie
from app.jwt import generate_token


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "createdAt": self.created_at,
        }

    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    def get_token(self):
        return generate_token(self.id)

    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        db.session.commit()


class Watchlist(db.Model):
    __tablename__ = "watchlist"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)

    def __repr__(self):
        return f"<Watchlist of {self.user_id}>"

    def get_movie(user_id):
        watchlist = (
            db.session.query(Movie)
            .join(Watchlist, Movie.id == Watchlist.movie_id)
            .filter(Watchlist.user_id == user_id)
            .all()
        )
        return [movie.to_dict() for movie in watchlist]

    def update_watchlist(user_id, movie_id):
        watchlist = Watchlist.query.filter_by(
            user_id=user_id, movie_id=movie_id
        ).first()
        if watchlist:
            db.session.delete(watchlist)
        else:
            new_watchlist = Watchlist(user_id=user_id, movie_id=movie_id)
            db.session.add(new_watchlist)

        db.session.commit()

    def populate_is_in_watchlist(movies, user_id):
        watchlist = Watchlist.query.filter_by(user_id=user_id).all()
        watchlist_ids = [movie.movie_id for movie in watchlist]

        for movie in movies:
            movie["is_in_watchlist"] = movie["id"] in watchlist_ids

        return movies


class Watched(db.Model):
    __tablename__ = "watched"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Watched of {self.user_id}>"

    def get_history(user_id):
        history = (
            db.session.query(Movie)
            .join(Watched, Movie.id == Watched.movie_id)
            .filter(Watched.user_id == user_id)
            .order_by(desc(Watched.created_at))
            .all()
        )
        return [movie.to_dict() for movie in history]

    def clear_history(user_id):
        history = Watched.query.filter_by(user_id=user_id).all()
        for movie in history:
            db.session.delete(movie)

        db.session.commit()

    def watch_movie(user_id, movie_id):
        watched = Watched.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if watched:
            watched.created_at = datetime.now(timezone.utc)
        else:
            new_watched = Watched(user_id=user_id, movie_id=movie_id)
            db.session.add(new_watched)

        db.session.commit()
