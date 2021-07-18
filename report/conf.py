import redis

redis_conn = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
