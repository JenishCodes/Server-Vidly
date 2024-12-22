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
