from pydantic import BaseSettings


class ResizerSettings(BaseSettings):
    tasks_queue_name: str

    class Config:
        env_file = 'app/resizer/.env'
        env_file_encoding = 'utf-8'


resizer_settings = ResizerSettings()
