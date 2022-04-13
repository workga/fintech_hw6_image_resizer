from typing import Optional

from redis.exceptions import RedisError
from rq import Queue
from rq.job import Job, JobStatus, NoSuchJobError

from app.logger import logger
from app.redis_db import redis_connection
from app.resizer.images import (
    base64_from_bytes,
    bytes_from_base64,
    bytes_from_image,
    image_from_bytes,
)
from app.resizer.schemas import ImageSize, TaskRead
from app.resizer.settings import resizer_settings


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


@redis_connection
def perform_task(task_id: int, conn) -> None:  # type: ignore
    key = encode_key(task_id, ImageSize.ORIGINAL)
    original_image_b = conn.get(key)

    if original_image_b is None:
        raise RedisError()

    for size in [ImageSize.SIZE_32, ImageSize.SIZE_64]:
        resized_image_b = resize_image(original_image_b, size)
        resized_image_b64 = base64_from_bytes(resized_image_b)

        key = encode_key(task_id, size)
        conn.set(key, resized_image_b64)

    logger.info('Task complete: task_id={task_id}')


@redis_connection
def add_task(image_b: bytes, conn) -> TaskRead:  # type: ignore
    task_id = conn.incr('last_task_id')
    key = encode_key(task_id, ImageSize.ORIGINAL)

    conn.set(key, image_b)

    queue = Queue(resizer_settings.tasks_queue_name, connection=conn)
    queue.enqueue(perform_task, task_id, job_id=str(task_id))

    logger.info(f'Task created: task_id = {task_id}')
    return TaskRead(task_id=task_id, task_status=JobStatus.QUEUED)


@redis_connection
def get_task(task_id: int, conn) -> Optional[TaskRead]:  # type: ignore
    logger.info(type(conn))
    try:
        job = Job.fetch(str(task_id), connection=conn)
    except NoSuchJobError:
        logger.error(f"Task doesn't exist: task_id = {task_id}")
        return None

    task_status = job.get_status(refresh=True)
    print(type(job))
    logger.info(f'Got task status: task_id = {task_id}, task_status = {task_status}')
    return TaskRead(task_id=task_id, task_status=task_status)


@redis_connection
def get_image(task_id: int, size: ImageSize, conn) -> Optional[bytes]:  # type: ignore
    task = get_task(task_id)  # type: ignore[call-arg]
    if task is None:
        logger.error(f"Task doesn't exist: task_id = {task_id}")
        return None

    if task.task_status != JobStatus.FINISHED:
        logger.error(
            f'Task is not finished: task_id = {task_id}, task_status = {task.task_status}'
        )
        return None

    key = encode_key(task_id, size)
    if size == ImageSize.ORIGINAL:
        image_b = conn.get(key)
        if image_b is None:
            raise RedisError()
    else:
        image_b64 = conn.get(key)
        if image_b64 is None:
            raise RedisError()
        image_b = bytes_from_base64(image_b64)

    logger.info(f'Got image: task_id = {task_id}')
    return image_b
