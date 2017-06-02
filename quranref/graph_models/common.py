"""
Common code used by various graph models
"""

from quranref import graph_models


def add_document_if_not_exists(document, collection=None,
                               update_if_exists=False, return_document='always',
                               use_db='gdb'):
    """
    return_document can have values: 'never', 'new' and 'always'
    """

    db = None
    if 'gdb' == use_db:
        db = graph_models.gdb
    elif 'vdb' == use_db:
        db = graph_models.vdb

    assert db is not None
    assert return_document in ['never', 'new', 'always']

    new_doc = None
    if isinstance(document, dict):
        assert collection is not None
        new_doc = collection(**document)
    else:
        new_doc = document

    if not db.exists(new_doc):
        db.add(new_doc)
        if return_document in ['new', 'always']:
            return new_doc

    else:
        if update_if_exists is True:
            db.update(new_doc)

        if 'always' == return_document:
            return db.query(new_doc.__class__).by_key(new_doc._key)

    return None


def update_document(document, use_db='gdb'):

    db = None
    if 'gdb' == use_db:
        db = graph_models.gdb
    elif 'vdb' == use_db:
        db = graph_models.vdb

    assert db is not None

    db.update(document)
