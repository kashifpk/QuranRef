from arango import ArangoClient
from arango_orm import Database

from .settings import get_settings


def db() -> Database:
    settings = get_settings()
    client = ArangoClient(hosts=settings.db_hosts)
    _db = client.db(settings.db_name, username=settings.db_username, password=settings.db_password)

    return Database(_db)
