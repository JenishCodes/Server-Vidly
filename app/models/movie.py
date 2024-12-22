from app import db


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512), nullable=False)
    poster = db.Column(db.String(1024), nullable=False)
    trailer = db.Column(db.String(1024), nullable=False)
    backdrop = db.Column(db.String(1024), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    runtime = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    cast = db.Column(db.String(1024), nullable=False)
    genres = db.Column(db.String(1024), nullable=False)
    director = db.Column(db.String(512), nullable=False)
    data = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(1024), nullable=False)
    watch_count = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Movie {self.title}>"

    def increase_watch_count(movie_id):
        movie = Movie.query.get(movie_id)
        movie.watch_count += 1
        db.session.commit()

    def get_movie(id):
        movie = Movie.query.get(id)
        return movie.to_dict() if movie else None

    def get_movies(ids):
        movies = Movie.query.filter(Movie.id.in_(ids)).all()
        movies_sorted = sorted(movies, key=lambda movie: ids.index(movie.id))

        return [movie.to_dict() for movie in movies_sorted]

    def get_trending_movie(limit=10):
        movies = Movie.query.order_by(Movie.watch_count.desc()).limit(limit).all()
        return [movie.to_dict() for movie in movies]

    def get_movies_data():
        data = Movie.query.order_by(Movie.id).with_entities(Movie.data).all()
        return [d[0] for d in data]

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "poster": self.poster,
            "trailer": self.trailer,
            "backdrop": self.backdrop,
            "year": self.year,
            "rating": self.rating,
            "runtime": self.runtime,
            "description": self.description,
            "cast": self.cast.split(","),
            "genres": self.genres.split(","),
            "director": self.director,
            "data": self.data,
            "link": self.link,
            "watch_count": self.watch_count,
        }
