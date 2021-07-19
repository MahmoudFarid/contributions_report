from .conf import redis_conn


class CacheMixin:
    def get_from_cache(self, cache_key):
        if redis_conn.hgetall(cache_key):
            print(f"Get this key: {cache_key} from the cache.")
            return redis_conn.hgetall(cache_key)

    def set_into_cache(self, cache_key, data):
        print(f"Set this key: {cache_key} into a cache.")
        redis_conn.hmset(cache_key, data)
