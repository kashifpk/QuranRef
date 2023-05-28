from arango import ArangoClient
from arango_orm import Database

from ..settings import get_settings


def get_gdb() -> Database:
    settings = get_settings()

    client = ArangoClient(hosts=f"http://{settings.gdb_host}:{settings.gdb_port}")
    db = client.db(
        settings.gdb_database, username=settings.gdb_username, password=settings.gdb_password
    )

    gdb = Database(db)

    return gdb
