import json
import os


class TrieNode:
    def __init__(self):
        self.children = {}
        self.movies = {}
        self.last = False


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.suggestions = {}
        self.dictionary = {}

        with open(os.path.abspath("./data/prefixes.json"), "r") as prefixes:
            data = json.load(prefixes)

            prefixes.close()

        self.form_trie(data)

    def insert(self, prefix, movies):
        node = self.root

        for a in list(prefix):
            if not node.children.get(a):
                node.children[a] = TrieNode()

            node = node.children[a]

        node.movies = movies
        node.last = True

    def form_trie(self, data):
        for prefix, movies in data.items():
            self.insert(prefix, movies)

    def traverse_rec(self, node, prefix):
        for char, n in node.children.items():
            if n.last:
                self.dictionary[prefix + char] = n.movies

            self.traverse_rec(n, prefix + char)

    def form_json(self):
        node = self.root
        self.traverse_rec(node, "")

        with open(os.path.abspath("./data/prefixes.json"), "w") as prefixes:
            json.dump(self.dictionary, prefixes)

            prefixes.close()

    def find_rec(self, node, movie_id):
        if node.last and node.movies.get(movie_id, -1) != -1:
            node.movies[movie_id] += 1
            return True
        else:
            for n in node.children.values():
                if self.find_rec(n, movie_id):
                    return True
            return False

    def increase_score(self, key, movie_id):
        node = self.root

        for a in list(key):
            node = node.children[a]

        self.find_rec(node, movie_id)

    def suggestion_rec(self, node):
        if node.last:
            self.suggestions.update(node.movies)

        for n in node.children.values():
            self.suggestion_rec(n)

    def get_auto_suggestions(self, key):
        node = self.root
        key = key.lower()

        for a in list(key):
            if not node.children.get(a):
                break

            node = node.children[a]

        self.suggestions = {}
        self.suggestion_rec(node)

        return self.suggestions
