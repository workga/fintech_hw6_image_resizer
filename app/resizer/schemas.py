from enum import Enum

from pydantic import BaseModel

from app.resizer.rqueue import TaskStatus


class ImageSize(Enum):
    SIZE_32 = '32'
    SIZE_64 = '64'
    ORIGINAL = 'original'


class TaskRead(BaseModel):
    task_id: int
    task_status: TaskStatus
