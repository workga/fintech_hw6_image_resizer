from typing import Optional

from app.logger import logger
from app.redis_db import redis_connection
from app.resizer import rqueue
from app.resizer.images import (
    base64_from_bytes,
    bytes_from_base64,
    bytes_from_image,
    image_from_bytes,
)
from app.resizer.schemas import ImageSize, TaskRead


def validate_image(image_b: bytes) -> bool:
    image = image_from_bytes(image_b)
    width, height = image.size
    return width == height


def resize_image(image_b: bytes, size: ImageSize) -> bytes:
    image = image_from_bytes(image_b)
    resized_image = image.resize((int(size.value), int(size.value)))
    resized_image_b = bytes_from_image(resized_image)

    return resized_image_b


def encode_key(task_id: int, size: ImageSize) -> str:
    return f'{task_id}_{size}'


def perform_task(task_id: int) -> None:
    with redis_connection() as conn:
        key = encode_key(task_id, ImageSize.ORIGINAL)
        original_image_b = conn.get(key)

        if original_image_b is None:
            raise RuntimeError('Original image not found.')

        for size in [ImageSize.SIZE_32, ImageSize.SIZE_64]:
            resized_image_b = resize_image(original_image_b, size)
            resized_image_b64 = base64_from_bytes(resized_image_b)

            key = encode_key(task_id, size)
            conn.set(key, resized_image_b64)

    logger.info(f'Task complete: task_id={task_id}')


def add_task(image_b: bytes) -> TaskRead:
    with redis_connection() as conn:
        task_id = conn.incr('last_task_id')

    key = encode_key(task_id, ImageSize.ORIGINAL)
    conn.set(key, image_b)

    rqueue.push_task(task_id, perform_task, task_id)

    logger.info(f'Task created: task_id = {task_id}')
    return TaskRead(task_id=task_id, task_status=rqueue.TaskStatus.QUEUED)


def get_task(task_id: int) -> Optional[TaskRead]:
    task_status = rqueue.get_task_status(task_id)
    if task_status is None:
        logger.error(f"Task doesn't exist: task_id = {task_id}")
        return None

    logger.info(f'Got task status: task_id = {task_id}, task_status = {task_status}')
    return TaskRead(task_id=task_id, task_status=task_status)


def get_image(task_id: int, size: ImageSize) -> Optional[bytes]:
    task = get_task(task_id)

    if task is None:
        logger.error(f"Task doesn't exist: task_id = {task_id}")
        return None

    if task.task_status != rqueue.TaskStatus.FINISHED:
        logger.error(
            f'Task is not finished: task_id = {task_id}, task_status = {task.task_status}'
        )
        return None

    key = encode_key(task_id, size)

    with redis_connection() as conn:
        image_b = conn.get(key)

    if size != ImageSize.ORIGINAL:
        # Because here we are sure that the image_b type is "bytes"
        image_b = bytes_from_base64(image_b)  # type: ignore

    logger.info(f'Got image: task_id = {task_id}')
    return image_b
