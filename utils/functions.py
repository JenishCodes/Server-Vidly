import os
import pandas as pd
import numpy as np

from gensim.corpora.dictionary import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.similarities.docsim import Similarity

from utils.trie import Trie


movies = pd.read_csv(os.path.abspath("./data/movies.csv"), index_col="id")

word_data = movies["data"].tolist()
processed_keywords = [keyword.split(",") for keyword in word_data]

dictionary = Dictionary(processed_keywords)  # Initialize Dictionary

corpus = [dictionary.doc2bow(doc) for doc in processed_keywords]  # Initialize Corpus

tfidf = TfidfModel(corpus)  # Initialize Tf-Idf Model

sims = Similarity(
    os.path.abspath("./data/sim_arr"),
    tfidf[corpus], num_features=len(dictionary)
)  # Initialize Similarity Matrix

trie = Trie()  # Initialize Trie


def get_recommendations(history):
    scores = [0 for _ in range(movies.shape[0])]
    
    for h in history:
        keywords = movies.loc[h].data
        scores = np.add(scores, get_movies_from_keywords(keywords, getMovies=False))
        
    scores = scores / len(history)
    indexes = movies.index.values.tolist()

    sorted_indexes = sorted(indexes, key=lambda x: scores[indexes.index(x)], reverse=True)
    sorted_scores = sorted(scores, reverse=True)
    
    for h in history:
        index = sorted_indexes.index(h)
        sorted_indexes.pop(index)
        sorted_scores.pop(index)
    
    top_movies = get_movies(sorted_indexes[:50])
    
    for i in range(50):
        top_movies[i]['score'] = sorted_scores[i]

    return top_movies


def get_movies(ids, dropRows=['data', 'keywords', 'tmdb']):
    res = movies.loc[ids]

    res['id'] = ids
    
    res = res.drop(dropRows, axis=1)

    res = res.to_dict('records')

    return res


def get_movie(movie_id, dropRows=['data', 'keywords', 'tmdb']):
    res = movies.loc[movie_id]
    
    res = res.drop(dropRows, axis=1)

    res = res.to_dict()

    res['id'] = movie_id

    return res


def get_suggestions(key, count=5):
    ids = trie.get_auto_suggestions(key)

    sorted_ids = sorted(ids, key=lambda x: ids[x], reverse=True)

    res = get_movies(sorted_ids[:count], ['data', 'keywords', 'tmdb', 'backdrop', 'description', 'trailer', 'duration', 'genres', 'link'])

    return res


def increase_movie_score(key, movie_id):
    trie.increase_score(key, movie_id)

    return None


def save_as_json():
    trie.form_json()


def get_movies_from_keywords(words, count=10, getMovies=True):
    word_list = words.split(",")
    query_doc_bow = dictionary.doc2bow(word_list)
    query_doc_tfidf = tfidf[query_doc_bow]

    sim_arr = sims[query_doc_tfidf]

    if getMovies:
        sim_scores = dict(zip(movies.index.values, sim_arr))

        movie_ids = sorted(sim_scores, key=lambda x: sim_scores[x], reverse=True)

        return movie_ids[:count]
    else:
        return sim_arr
