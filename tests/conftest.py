from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.app import create_app

from redis import Connection


@pytest.fixture(name='app')
def fixture_app():
    return create_app()


@pytest.fixture(name='client')
def fixture_client(app):
    return TestClient(app)


@pytest.fixture(name='mocked_redis', autouse=True)
def fixture_mocked_redis(mocker):
    return mocker.patch("app.redis_db.redis.Redis", spec=True)
    


# @pytest.fixture(name='mocked_redis', autouse=True)
# def fixture_mocked_redis(mocker, redisdb):
#     mocker.patch("redis.Redis", new = redisdb)





# @pytest.fixture(name='mocked_queue', autouse=True)
# def fixture_mocked_queue(mocker):
#     mocked_queue = mocker.patch("rq.Queue")
    
#     return mocked_queue

# @pytest.fixture(name='mocked_job', autouse=True)
# def fixture_mocked_job(mocker):
   
#     return mocked_job

