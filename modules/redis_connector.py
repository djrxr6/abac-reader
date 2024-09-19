import redis


class RedisConnector:
    rd = ""
    host, port = "192.168.1.117", 6379

    def __init__(self) -> None:
        self.rd = redis.Redis(self.host, self.port, decode_responses=True)

    def get_redis_object(self) -> redis:
        return self.rd
