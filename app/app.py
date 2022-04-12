from fastapi import FastAPI, Request, Response

from redis.exceptions import RedisError
from app.resizer.routes import router as resizer_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(resizer_router, prefix='/resizer')

    @app.exception_handler(RedisError)
    def handle_db_exceptions(request: Request, exception: RedisError):
        return Response(status_code=500)

    return app
