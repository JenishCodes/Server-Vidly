from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .movie import Movie


class Recommender:
    _recommendar = None

    def __new__(cls):
        if not cls._recommendar:
            cls._recommendar = super(Recommender, cls).__new__(cls)
        return cls._recommendar

    def __init__(self):
        data = Movie.get_movies_data()

        self.vectorizer = TfidfVectorizer()
        self.tfidf = self.vectorizer.fit_transform(data)

        print("Recommender loaded successfully!")

    def get_similar_movies(self, words, limit):
        query_vector = self.vectorizer.transform([words])

        sims = cosine_similarity(query_vector, self.tfidf).flatten()

        movies = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)

        movie_ids = [movie_id + 1 for movie_id, _ in movies][1 : limit + 1]

        return Movie.get_movies(movie_ids)

    def get_recommended_movies(self, watched, limit=50):
        watched_ids, sims = [], []

        for id, data in watched.items():
            watched_ids.append(id)

            query_vector = self.vectorizer.transform([data])
            temp_sims = cosine_similarity(query_vector, self.tfidf).flatten()

            if len(sims) == 0:
                sims = [x for x in temp_sims]
            else:
                sims = [x + y for x, y in zip(sims, temp_sims)]

        min_sim, max_sim = min(sims), max(sims)
        sims = [(sim - min_sim) / (max_sim - min_sim) for sim in sims]

        for id in watched_ids:
            sims[id] = -1

        movies = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)

        movie_ids = [movie_id for movie_id, _ in movies][:limit]

        return Movie.get_movies(movie_ids)
