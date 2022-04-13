from fastapi import FastAPI, Request, Response
from redis.exceptions import RedisError

from app.resizer.routes import router as resizer_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(resizer_router, prefix='/resizer')

    # Because this decorator needs a function with such arguments
    @app.exception_handler(RedisError)
    def handle_db_exceptions(
        request: Request, exception: RedisError  # pylint: disable=unused-argument
    ) -> Response:
        return Response(status_code=500)

    return app
