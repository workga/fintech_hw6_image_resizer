from typing import Any, Callable

from rq import Queue
from rq.job import Job, JobStatus, NoSuchJobError
from typing_extensions import TypeAlias

from app.redis_db import redis_connection
from app.resizer.settings import resizer_settings

TaskStatus: TypeAlias = JobStatus


def push_task(task_id: int, func: Callable[..., Any], *args: int) -> None:
    with redis_connection() as conn:
        queue = Queue(resizer_settings.tasks_queue_name, connection=conn)
        queue.enqueue(func, *args, job_id=str(task_id))


def get_task_status(task_id: int) -> TaskStatus:
    try:
        with redis_connection() as conn:
            job = Job.fetch(str(task_id), connection=conn)
    except NoSuchJobError:
        return None

    return job.get_status()
