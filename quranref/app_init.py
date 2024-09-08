"""
Application wide initialization logic.

This is used by both api and non api processes like celery tasks, cli commands etc.
"""

from .log_config import configure_logging


def app_init():
    configure_logging()
    # app_globals_init()


def app_cleanup():
    # app_globals_cleanup()
    pass
