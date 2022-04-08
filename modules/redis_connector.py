import redis

class RedisConnector:
    rd = ''
    host, port = '192.168.1.117',6379

    def __init__(this) -> None:
        this.rd = redis.Redis(this.host, this.port, decode_responses=True)

    def get_redis_object(this) -> redis:
        return this.rd
