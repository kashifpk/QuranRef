"""
Common code used by various graph models
"""

import logging
from quranref import graph_models

log = logging.getLogger(__name__)


def add_document_if_not_exists(document, collection=None,
                               update_if_exists=False, return_document='always'):
    """
    return_document can have values: 'never', 'new' and 'always'
    """

    db = graph_models.get_gdb()

    assert return_document in ['never', 'new', 'always']

    # log.debug("trying to add document: %s\n%r", document.__collection__, document._dump())
    new_doc = None
    if isinstance(document, dict):
        assert collection is not None
        new_doc = collection(**document)
    else:
        new_doc = document

    if not db.exists(new_doc):
        # log.debug(" --> document does not exist, adding")
        db.add(new_doc)
        if return_document in ['new', 'always']:
            return new_doc

    else:
        # log.debug(" --> Document exists")
        if update_if_exists is True:
            db.update(new_doc)

        if 'always' == return_document:
            return db.query(new_doc.__class__).by_key(new_doc._key)

    return None
