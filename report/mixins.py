from .conf import redis_conn


class CacheMixin:
    def get_from_cache(self, cache_key: str) -> dict:
        """Will return a value from the cache_key if it exists.

        Args:
            - cache_key(str): The cache key

        Return:
            - dict: with the results
        """
        if redis_conn.hgetall(cache_key):
            print(f"Get this key: {cache_key} from the cache.")
            return redis_conn.hgetall(cache_key)

    def set_into_cache(self, cache_key: str, data: dict) -> None:
        """Add the data into a cach key.

        Args:
            - cache_key(str): The cache key.
            - data(dict): The data will be cached.
        """
        print(f"Set this key: {cache_key} into a cache.")
        redis_conn.hmset(cache_key, data)
