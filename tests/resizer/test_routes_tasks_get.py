import pytest
from redis import RedisError
from rq.job import JobStatus, NoSuchJobError


@pytest.mark.parametrize(
    'job_status',
    [
        JobStatus.QUEUED,
        JobStatus.STARTED,
        JobStatus.FINISHED,
        JobStatus.FAILED,
    ],
)
def test_success(client, mocked_job, job_status):
    mocked_job.fetch.return_value.get_status.return_value = job_status

    response = client.get('/resizer/tasks/10')

    assert response.status_code == 200

    data = response.json()
    assert data['task_id'] == 10
    assert data['task_status'] == job_status.value


@pytest.mark.parametrize(
    'task_id',
    [
        0,
        -1,
        None,
        'a',
    ],
)
def test_fail_invalid_params(client, task_id):
    response = client.get(f'/resizer/tasks/{task_id}')

    assert response.status_code == 422


def test_fail_task_not_exists(client, mocked_job):
    mocked_job.fetch.side_effect = NoSuchJobError

    response = client.get('/resizer/tasks/10')

    assert response.status_code == 404


def test_fail_redis_error(client, mocked_redis):
    mocked_redis.side_effect = RedisError

    response = client.get('/resizer/tasks/10')

    assert response.status_code == 500
