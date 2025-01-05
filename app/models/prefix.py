from app import db


class Prefix(db.Model):
    __tablename__ = "prefix"

    id = db.Column(db.Integer, primary_key=True)
    prefix = db.Column(db.String(256), nullable=False)

    movies = db.relationship("PrefixMovie", backref="prefix")

    def __repr__(self):
        return f"<Prefix {self.prefix}>"

    def get_all_prefix():
        result = {}
        prefixes = Prefix.query.all()

        for prefix in prefixes:
            result[prefix.prefix] = prefix.get_movies()

        return result

    def get_movies(self):
        movies = {}
        for movie in self.movies:
            movies[movie.movie_id] = movie.score

        return movies

    def save(self):
        db.session.add(self)
        db.session.commit()

        return self


class PrefixMovie(db.Model):
    __tablename__ = "prefix_movie"

    id = db.Column(db.Integer, primary_key=True)
    prefix_id = db.Column(db.Integer, db.ForeignKey("prefix.id"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"))
    score = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<PrefixMovie {self.prefix_id} - {self.movie_id}>"

    def update_score(prefix, movie_id, score):
        prefix_movie = (
            db.session.query(PrefixMovie)
            .join(Prefix, Prefix.id == PrefixMovie.prefix_id)
            .filter(Prefix.prefix.like(f"{prefix}%"), PrefixMovie.movie_id == movie_id)
            .first()
        )

        if not prefix_movie:
            return None

        prefix_movie.score += score
        db.session.commit()
    
    def save(self):
        db.session.add(self)
        db.session.commit()

        return self
