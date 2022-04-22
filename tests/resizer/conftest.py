import pytest


@pytest.fixture(name='mocked_queue', autouse=True)
def fixture_mocked_queue(mocker):
    return mocker.patch('app.resizer.rqueue.Queue', spec=True)


@pytest.fixture(name='mocked_job', autouse=True)
def fixture_mocked_job(mocker):
    return mocker.patch('app.resizer.rqueue.Job', spec=True)
