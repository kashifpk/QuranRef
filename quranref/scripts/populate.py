import os
import sys

from pyramid.paster import get_appsettings, setup_logging

from .. import load_project_settings, do_config


def usage(argv):
    cmd = os.path.basename(argv[0])
    print(('usage: %s <config_uri>\n'
           '(example: "%s development.ini")' % (cmd, cmd)))
    sys.exit(1)


def _get_graph():
    from ..graph_models import gdb
    from ..graph_models.quran_graph import QuranGraph
    graph = QuranGraph(connection=gdb)

    return gdb, QuranGraph, graph


def create_graph():
    gdb, _, graph = _get_graph()
    gdb.create_graph(graph)


def main(argv=sys.argv):  # pylint: disable=W0102

    if len(argv) != 2:
        usage(argv)

    load_project_settings()

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    do_config({'__file__': config_uri}, **settings)

    # create_graph()
    gdb, QuranGraph, _ = _get_graph()
    db_objects = [QuranGraph]
    gdb.create_all(db_objects)

