import json
from enum import Enum

from confluent_kafka import Producer as MessageProducer

from app.config import Config
from app.redis import redis_client
from app.models import PrefixMovie


class Producer:
    _producer = None

    def __new__(cls):
        if not cls._producer:
            cls._producer = super(Producer, cls).__new__(cls)
        return cls._producer

    def __init__(self):
        self.message_producer = MessageProducer({
            'bootstrap.servers': Config.KAFKA_BROKER_URL,
        })
    
    def send_message(self, topic, message):
        self.message_producer.produce(topic, value=json.dumps(message))
        self.message_producer.flush()
    
    def close(self):
        self.message_producer.flush()
        self.message_producer.close()


class Topic(Enum):
    UPDATE_SEARCH_SCORE = "update_search_score"

    def get_all_topics():
        return [topic.value for topic in Topic]

    def publish(self, message):
        producer = Producer()
        producer.send_message(self.value, message)
    
    def process(self, _):
        if self == Topic.UPDATE_SEARCH_SCORE:
            self.update_search_score()
        else:
            raise Exception("Invalid topic")
    
    def update_search_score(self):
        nodes = redis_client.hgetall("trie:pending_nodes")

        redis_client.delete("trie:pending_nodes")
        redis_client.set("trie:pending_node_count", 0)
        
        for key, value in nodes.items():
            movie_id, prefix = key.split(":")
            score = int(value)
            
            PrefixMovie.update_score(prefix, int(movie_id), score)
