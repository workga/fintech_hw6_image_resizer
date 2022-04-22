from contextlib import contextmanager
from typing import Iterator

import redis
from redis.exceptions import RedisError

from app.logger import logger
from app.settings import app_settings

connection_pool = redis.ConnectionPool(
    host=app_settings.redis_host,
    port=app_settings.redis_port,
    db=0,
)


@contextmanager
def redis_connection() -> Iterator[redis.Redis]:  # type: ignore
    try:
        yield redis.Redis(connection_pool=connection_pool)
    except RedisError as error:
        logger.error(error)
        raise
