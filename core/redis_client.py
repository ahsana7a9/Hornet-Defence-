import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def publish(channel, data):
    r.publish(channel, json.dumps(data))

def subscribe(channel):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    return pubsub
