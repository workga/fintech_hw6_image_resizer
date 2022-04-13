import pytest


@pytest.fixture(name='mocked_queue', autouse=True)
def fixture_mocked_queue(mocker):
    return mocker.patch('app.resizer.resizer.Queue', spec=True)


@pytest.fixture(name='mocked_job', autouse=True)
def fixture_mocked_job(mocker):
    return mocker.patch('app.resizer.resizer.Job', spec=True)
