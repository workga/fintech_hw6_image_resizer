import pytest
from PIL import Image
from rq.job import Job

from app.resizer.images import bytes_from_image


@pytest.mark.parametrize(
    ('size', 'content_type', 'status'),
    [
        ((10, 10), 'image/jpeg', 201),
        ((10, 11), 'image/jpeg', 422),
        ((10, 10), 'image/png', 415),
        ((10, 10), 'application/json', 400),
    ],
)
def test_routes_tasks_post(client, size, content_type, status):
    image = Image.new(mode='RGB', size=size)
    image_b = bytes_from_image(image)

    response = client.post(
        '/resizer/tasks', data=image_b, headers={'content-type': content_type}
    )

    assert response.status_code == status


@pytest.mark.parametrize(
    ('task_id', 'status'),
    [
        (10, 'queued'),
    ],
)
def test_routes_tasks_get_success(mocker, client, task_id, status):
    mocker.patch('rq.job.Job.fetch', return_value=Job(id=str(task_id)))
    mocker.patch('rq.job.Job.get_status', return_value=status)

    response = client.post(f'/resizer/tasks/{task_id}')

    assert response.status_code == 200

    data = response.json()
    assert data['task_id'] == task_id
    assert data['status'] == status
