import redis
from .settings import settings

# 条件性添加密码参数
redis_config = {
    "host": settings.REDIS_HOST,
    "port": settings.REDIS_PORT,
    "db": settings.REDIS_DB
}
if settings.REDIS_PASSWORD:
    redis_config["password"] = settings.REDIS_PASSWORD

redis_client = redis.Redis(**redis_config)

def get_redis_client():
    return redis_client
