import logging

from arango import ArangoClient
from arango_orm import Database

log = logging.getLogger(__name__)

gdb = None

def connect(server, port, username, password, db_name):

    global gdb

    client = ArangoClient(host=server, port=port, username=username, password=password)
    db = client.db(db_name)

    gdb = Database(db)

    return gdb
