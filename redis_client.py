# redis_client.py
# Singleton pattern for Redis client, to ensure there's only one instance
# shared across the application.

import redis
class RedisClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            # Defaults to localhost, port 6379
            cls._instance = redis.Redis()
        return cls._instance

# Usage
# redis_client = RedisClient.get_instance()
