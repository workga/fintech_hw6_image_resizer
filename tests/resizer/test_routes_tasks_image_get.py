import pytest
from contextlib import nullcontext as does_not_raise
from redis import RedisError

from rq.job import JobStatus, NoSuchJobError

from app.resizer.schemas import ImageSize
from PIL import Image
from app.resizer.images import base64_from_bytes, bytes_from_image, image_from_bytes

@pytest.mark.parametrize(
    'size', [
        ImageSize.ORIGINAL,
        ImageSize.SIZE_32,
        ImageSize.SIZE_64,
        None,
    ]
)
def test_success(client, mocked_job, mocked_redis, size):
    mocked_job.fetch.return_value.get_status.return_value = JobStatus.FINISHED
    
    image = Image.new(mode='RGB', size=(10, 10))
    image_b = bytes_from_image(image)

    if size == ImageSize.ORIGINAL:
        mocked_redis.return_value.get.return_value = image_b
    else:
        mocked_redis.return_value.get.return_value = base64_from_bytes(image_b)
    
    if size is not None:
        response = client.get(f'/resizer/tasks/10/image?size={size.value}')
    else:
        response = client.get(f'/resizer/tasks/10/image')

    assert response.status_code == 200
    try:
        image_from_bytes(response.content)
    except Exception as error:
        assert False


@pytest.mark.parametrize(
    ('task_id', 'size'), [
        (0, ImageSize.ORIGINAL),
        (-1, ImageSize.ORIGINAL),
        (None, ImageSize.ORIGINAL),
        ('a', ImageSize.ORIGINAL),
        (1, 0),
        (1, -1),
        (1, 10),
        (1, None),
        (1, ''),
        (1, 'a'),
    ])
def test_fail_invalid_params(client, task_id, size):
    response = client.get(f'/resizer/tasks/{task_id}/image?size={size}')

    assert response.status_code == 422


def test_fail_task_not_exists(client, mocked_job):
    mocked_job.fetch.side_effect = NoSuchJobError


    response = client.get(f'/resizer/tasks/10/image')

    assert response.status_code == 404


@pytest.mark.parametrize(
    'job_status', [
        JobStatus.QUEUED,
        JobStatus.STARTED,
        JobStatus.FAILED,
])
def test_fail_task_not_finished(client, mocked_job, job_status):
    mocked_job.fetch.return_value.get_status.return_value = job_status


    response = client.get(f'/resizer/tasks/10/image')

    assert response.status_code == 404


def test_fail_redis_error(client, mocked_redis):
    mocked_redis.side_effect = RedisError

    response = client.get(f'/resizer/tasks/10/image')

    assert response.status_code == 500