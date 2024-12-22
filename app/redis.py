from flask_redis import FlaskRedis

redis_client = FlaskRedis(decode_responses=True)


def configure_redis(app):
    redis_client.init_app(app)
