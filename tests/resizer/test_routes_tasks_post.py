from PIL import Image
from redis import RedisError

from app.resizer.images import bytes_from_image


def test_success(client):
    image = Image.new(mode='RGB', size=(10, 10))
    image_b = bytes_from_image(image)

    response = client.post(
        '/resizer/tasks', data=image_b, headers={'content-type': 'image/jpeg'}
    )

    assert response.status_code == 201


def test_fail_wrong_size(client):
    image = Image.new(mode='RGB', size=(10, 11))
    image_b = bytes_from_image(image)

    response = client.post(
        '/resizer/tasks', data=image_b, headers={'content-type': 'image/jpeg'}
    )

    assert response.status_code == 422


def test_fail_wrong_image_type(client):
    image = Image.new(mode='RGB', size=(10, 10))
    image_b = bytes_from_image(image)

    response = client.post(
        '/resizer/tasks', data=image_b, headers={'content-type': 'image/png'}
    )

    assert response.status_code == 415


def test_fail_wrong_content_type(client):
    image = Image.new(mode='RGB', size=(10, 10))
    image_b = bytes_from_image(image)

    response = client.post(
        '/resizer/tasks', data=image_b, headers={'content-type': 'application/json'}
    )

    assert response.status_code == 400


def test_fail_redis_error(client, mocked_redis):
    mocked_redis.side_effect = RedisError

    image = Image.new(mode='RGB', size=(10, 10))
    image_b = bytes_from_image(image)

    response = client.post(
        '/resizer/tasks', data=image_b, headers={'content-type': 'image/jpeg'}
    )

    assert response.status_code == 500
