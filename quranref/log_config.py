from logging.config import dictConfig

from dotenv import dotenv_values

from . import PROJECT_ROOT

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",

        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "show_path": True,
        },
    },
    "loggers": None
}


def configure_logging():

    loggers_dict = {}
    env_file = PROJECT_ROOT / ".env"
    env_vals = dotenv_values(str(env_file))
    log_packages = env_vals.get("LOGGING_ENABLED_FOR_PACKAGES", "quranref").split(",")

    for log_package in log_packages:
        package_name, log_level = log_package.split(":")
        loggers_dict[package_name] = {"handlers": ["default"], "level": log_level}

    log_config["loggers"] = loggers_dict
    dictConfig(log_config)
