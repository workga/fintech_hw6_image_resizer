from ctypes import resize
from http.client import IM_USED
from PIL import Image
from pyparsing import Or
import pytest
from redis import RedisError
from app.resizer.images import bytes_from_image, image_from_bytes
from app.resizer import resizer
from app.resizer.schemas import ImageSize


@pytest.mark.parametrize(
    ('old_size', 'new_size'), [
        (10, ImageSize.SIZE_32),
        (10, ImageSize.SIZE_64),
        (100, ImageSize.SIZE_32),
        (100, ImageSize.SIZE_64),
    ]
)
def test_resize_image_success(old_size, new_size):
    image = Image.new(mode='RGB', size=(old_size, old_size))
    image_b = bytes_from_image(image)

    resized_image_b = resizer.resize_image(image_b, new_size)
    resized_image = image_from_bytes(resized_image_b)
    

    assert resized_image.size == (int(new_size.value), int(new_size.value))


def test_perform_task_success(mocked_redis):
    image = Image.new(mode='RGB', size=(10, 10))
    image_b = bytes_from_image(image)

    mocked_redis.return_value.get.return_value = image_b

    try:
        resizer.perform_task(10)
    except Exception as error:
        assert False


def test_perform_task_fail_redis_error(mocked_redis):
    mocked_redis.return_value.get.side_effect = RedisError

    with pytest.raises(RedisError):
        resizer.perform_task(10)


