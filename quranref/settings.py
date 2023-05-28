from functools import lru_cache

from pydantic import BaseSettings, Field
from . import PROJECT_ROOT


class Settings(BaseSettings):

    class Config:
        env_file = PROJECT_ROOT / ".env"

    app_name: str = "QuranRef"
    environment: str = Field(env='ENVIRONMENT')
    debug: bool = Field(False, env="CHIRPSTACK_USE_SECURE_CHANNEL")
    gdb_host: str = Field("localhost", env="GDB_SERVER")
    gdb_port: int = Field(8529, env="GDB_PORT")
    gdb_username: str = Field(env="GDB_USERNAME")
    gdb_password: str = Field(env="GDB_PASSWORD")
    gdb_database: str = Field(env="GDB_DATABASE")


@lru_cache
def get_settings():
    return Settings()
