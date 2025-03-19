from functools import lru_cache
from typing import Any

from dotenv import dotenv_values
from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import PROJECT_ROOT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra='allow')

    app_name: str = "QuranRef"
    environment: str = Field(..., env="ENVIRONMENT")
    in_docker: bool = Field(False, env="AM_I_DOCKERIZED")
    # website_base_url: str = Field(..., env="WEBSITE_BASE_URL")
    # dev_js_server: str = Field("", env="DEV_JS_SERVER")
    # static_url: str = Field(..., env="STATIC_URL")

    db_username: str = Field(..., env="DB_USERNAME")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_name: str = Field(..., env="DB_NAME")

    db_hosts_normal: str = Field(..., env="DB_HOSTS_NORMAL")
    db_hosts_docker: str = Field(..., env="DB_HOSTS_DOCKER")

    @property
    def db_hosts(self) -> str:
        if self.in_docker:
            return self.db_hosts_docker

        return self.db_hosts_normal

    debug: bool = False

    @field_validator("debug", mode="before")
    @classmethod
    def determine_debug_mode(cls, v: bool | None, vinfo: ValidationInfo) -> bool:
        if isinstance(v, bool):
            return v

        if vinfo.data["environment"] == "development":
            return True

        return False

    @field_validator("*", mode='before')
    @classmethod
    def use_testing_config(cls, v: Any, vinfo: ValidationInfo) -> Any:
        # settings.__class__.model_fields['db_name'].json_schema_extra
        if vinfo.data.get("environment", "") == "testing":
            if cls.model_fields[vinfo.field_name].json_schema_extra is None:
                return v

            env_var = cls.model_fields[vinfo.field_name].json_schema_extra.get("env", None)
            if env_var:
                testing_env_var = "testing_" + env_var
                env_file_values = dotenv_values(cls.model_config['env_file'])
                return env_file_values.get(testing_env_var, v)

        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
