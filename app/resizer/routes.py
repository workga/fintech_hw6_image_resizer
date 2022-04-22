from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)

from app.resizer import resizer
from app.resizer.schemas import ImageSize, TaskRead
from app.resizer.utils import content_type_jpeg

router = APIRouter()


@router.post(
    '/tasks',
    dependencies=[Depends(content_type_jpeg)],
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def tasks_post(image_b: bytes = Body(..., media_type='image/jpeg')) -> TaskRead:
    if not resizer.validate_image(image_b):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    task = resizer.add_task(image_b)

    return task


@router.get('/tasks/{task_id}', response_model=TaskRead, status_code=status.HTTP_200_OK)
def tasks_get(task_id: int = Path(..., ge=1)) -> TaskRead:
    task = resizer.get_task(task_id)
    if task is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
        )

    return task


@router.get(
    '/tasks/{task_id}/image',
    response_class=Response,
    status_code=status.HTTP_200_OK,
    responses={200: {'content': {'image/png': {}}}},
)
def tasks_image_get(
    task_id: int = Path(..., ge=1),
    size: ImageSize = Query(ImageSize.SIZE_32),
) -> Response:
    image_b = resizer.get_image(task_id, size)
    if image_b is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
        )

    return Response(content=image_b, media_type='image/jpeg')
