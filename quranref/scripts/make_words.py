import os
import sys
import logging

from pyramid.paster import get_appsettings, setup_logging

from .. import load_project_settings, do_config

log = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print(('usage: %s <config_uri>\n'
           '(examples:\n    "%s development.ini")' % (cmd, cmd)))
    sys.exit(1)


def make_words():  # pylint: disable=R0914

    from ..graph_models import gdb
    from ..graph_models.common import add_document_if_not_exists
    from ..graph_models.quran_graph import Aya, Word, Has, QuranGraph

    qgraph = QuranGraph(connection=gdb)

    ayas = gdb.query(Aya).all()
    for aya in ayas:
        if 0 == aya.aya_number:
            continue

        aql = """
        FOR v, e, p IN 1..2 OUTBOUND 'ayas/{}' GRAPH 'quran_graph'
            FILTER p.edges[0].text_type=="simple-clean"
        RETURN p
        """.format(aya._key)

        obj = qgraph.aql(aql)

        log.debug("processing %r", obj._dump())

        aya_text = obj._relations['aya_texts'][0]._next.text
        aya_words = aya_text.split(' ')
        # log.debug(aya_words)

        for word in aya_words:
            word_doc = add_document_if_not_exists(Word.new(word=word))
            has_key = "AW-{}-{}".format(aya._key, word_doc._key)
            has_document = qgraph.relation(aya, Has(_key=has_key), word_doc)
            add_document_if_not_exists(has_document, return_document='never')

    log.info("Done importing!")


def main(argv=sys.argv):  # pylint: disable=W0102
    if len(argv) != 2:
        usage(argv)

    load_project_settings()

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    do_config({'__file__': config_uri}, **settings)

    make_words()
