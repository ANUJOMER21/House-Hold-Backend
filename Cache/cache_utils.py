import redis
import json

# Initialize Redis connection (modify host and port as per your setup)
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

def cache_data(key, fetch_function, expiration=60):

    # Try fetching data from Redis
    cached_data = redis_client.get(key)
    if cached_data:
        return cached_data

    # If no cache, fetch fresh data, cache it, and return
    fresh_data = fetch_function()
    redis_client.setex(key, expiration, json.dumps(fresh_data))  # Serialize fresh data to JSON
    return json.dumps(fresh_data)
