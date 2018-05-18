import logging

from arango import ArangoClient
from arango_orm import Database

log = logging.getLogger(__name__)

gdb = None

def connect(server, port, username, password, db_name):

    global gdb

    client = ArangoClient(host=server, port=port)
    db = client.db(db_name, username=username, password=password)

    gdb = Database(db)

    return gdb
