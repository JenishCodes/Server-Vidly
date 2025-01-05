from .movie import Movie
from .prefix import Prefix
from app.config import Config
from app.producer import Topic
from app.redis import redis_client


class Trie:
    trie = None
    root_id = "trie:node:0"

    def __new__(cls):
        if not cls.trie:
            cls.trie = super(Trie, cls).__new__(cls)
        return cls.trie

    def __init__(self):
        is_built = redis_client.get(Trie.root_id)
        if is_built:
            return print("Trie already built!")
        
        self.build_trie()
        print("Trie built successfully!")

    def build_trie(self):
        redis_client.set(Trie.root_id, 1)

        prefixes = Prefix.get_all_prefix()
        for prefix, movies in prefixes.items():
            self.insert_prefix(prefix, movies)

    def create_node(self):
        node_id = redis_client.incr("trie:node:counter")

        redis_client.hset(f"trie:node:{node_id}", mapping={"is_end": 0})
        redis_client.delete(f"trie:node:{node_id}:children")
        redis_client.delete(f"trie:node:{node_id}:movies")

        return node_id

    def set_is_end(self, node_id, is_end=1):
        redis_client.hset(f"trie:node:{node_id}", mapping={"is_end": is_end})

    def get_is_end(self, node_id):
        return redis_client.hget(f"trie:node:{node_id}", "is_end")

    def add_child(self, node_id, char, child_id):
        redis_client.hset(f"trie:node:{node_id}:children", char, child_id)

    def get_children(self, node_id):
        return redis_client.hgetall(f"trie:node:{node_id}:children")

    def add_movies(self, node_id, movies):
        redis_client.hset(f"trie:node:{node_id}:movies", mapping=movies)

    def get_movies(self, node_id):
        return redis_client.hgetall(f"trie:node:{node_id}:movies")

    def get_child(self, node_id, char):
        return redis_client.hget(f"trie:node:{node_id}:children", char)

    def sync_to_db(self, prefix, movie_id):
        movie_score = redis_client.hget(f"trie:pending_nodes", f"{movie_id}:{prefix}")
        if movie_score:
            movie_score = int(movie_score)
        else:
            movie_score = 0

        redis_client.hset(
            f"trie:pending_nodes", f"{movie_id}:{prefix}", movie_score + 1
        )

        pending_node_count = redis_client.incr("trie:pending_node_count")
        if pending_node_count >= Config.REDIS_PENDING_NODE_THRESHOLD:
            Topic.UPDATE_SEARCH_SCORE.publish(None)

    def increment_search_count(self, prefix, movie_id):
        node_id = 0
        for char in prefix:
            child_id = self.get_child(node_id, char)
            if not child_id:
                break

            node_id = child_id

        nodes = [("", node_id)]
        while nodes:
            (postfix, node_id) = nodes.pop(0)

            if self.get_is_end(node_id) == "1":
                movies = self.get_movies(node_id)

                if movie_id in movies:
                    score = int(movies[movie_id])
                    redis_client.hset(
                        f"trie:node:{node_id}:movies", movie_id, score + 1
                    )
                    prefix = prefix + postfix
                    break

            children = self.get_children(node_id)
            for char, child_id in children.items():
                nodes.append((postfix + char, child_id))

        return self.sync_to_db(prefix, movie_id)

    def insert_prefix(self, prefix, movies):
        node_id = 0
        for char in prefix:
            child_id = self.get_child(node_id, char)
            if not child_id:
                child_id = self.create_node()
                self.add_child(node_id, char, child_id)
            node_id = child_id

        self.set_is_end(node_id)
        self.add_movies(node_id, movies)

    def search_movies(self, node_id):
        movies = {}
        if self.get_is_end(node_id) == "1":
            movies = self.get_movies(node_id)

        children = self.get_children(node_id)

        for child_id in children.values():
            child_movies = self.search_movies(child_id)
            movies.update(child_movies)

        return movies

    def search_prefix(self, prefix, limit):
        node_id = 0
        for char in prefix:
            child_id = self.get_child(node_id, char)
            if not child_id:
                break

            node_id = child_id

        movies = self.search_movies(node_id)

        results = [
            int(movie)
            for movie, _ in sorted(movies.items(), key=lambda x: x[1], reverse=True)
        ]

        return Movie.get_movies(results[:limit])
