from .movie import Movie
from .prefix import Prefix, PrefixMovie
from .user import User, Watched, Watchlist

trie = None
recommender = None


def load_recommender():
    global recommender
    from .recommender import Recommender

    recommender = Recommender()


def build_trie():
    global trie
    from .trie import Trie

    trie = Trie()


def load_data():
    import json

    if Movie.query.count() > 0:
        return print("Data already loaded!")

    movies = []
    with open("app/data/movies.json", "r") as f:
        movies = json.load(f)

    print("Loading data into database...")
    for m in movies:
        movie = Movie(**m).save()

        title = " " + movie.title.lower()

        i = 0
        while i < len(title):
            if title[i] == " ":
                p = Prefix.query.filter_by(prefix=title[i+1:]).first()
                if not p:
                    p = Prefix(prefix=title[i+1:]).save()
                    
                PrefixMovie(prefix_id=p.id, movie_id=movie.id).save()
                
            i += 1
                
    print("Data loaded successfully!")    