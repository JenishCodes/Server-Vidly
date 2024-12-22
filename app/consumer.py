import json

from confluent_kafka import Consumer as MessageConsumer

from app.config import Config
from app.producer import Topic


class Consumer:
    _consumer = None
    _running = False

    def __new__(cls):
        if not cls._consumer:
            cls._consumer = super(Consumer, cls).__new__(cls)

        return cls._consumer

    def __init__(self):
        Consumer._running = True

        self.message_consumer = MessageConsumer(
            {
                "bootstrap.servers": Config.KAFKA_BROKER_URL,
                "group.id": "consumer_group",
                "auto.offset.reset": "earliest",
            }
        )

    def subscribe(self, topics):
        self.message_consumer.subscribe(topics)

    def poll(self):
        return self.message_consumer.poll(1.0)

    def start_consumer(self, context):
        with context():
            self.subscribe(Topic.get_all_topics())

            while Consumer._running:
                message = self.poll()
                if message is None:
                    continue
                elif message.error():
                    print(f"Consumer error: {message.error()}")
                    continue

                data = json.loads(message.value().decode("utf-8"))

                Topic(message.topic()).process(data)

    def shutdown(self):
        Consumer._running = False
        self.message_consumer.close()
