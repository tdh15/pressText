# add_message_to_send_queue.py
# Manage the queue of messages to send to users

from redis_client import RedisClient
import json

def add_message_to_send_queue(message, phone_number):
    redis_client = RedisClient.get_instance()
    # Serialize info as a json object
    item = json.dumps({"message": message, "phone_number": phone_number})
    # Use Redis 'lpush' to add message to the list
    redis_client.lpush('send_queue', item)
    print(f'Message added to queue: \"{message}\"')