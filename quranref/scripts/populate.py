import os
import sys
# import importlib

from pyramid.paster import get_appsettings, setup_logging

# from ..apps import enabled_apps
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

    return gdb, graph


def create_graph():
    gdb, graph = _get_graph()
    gdb.create_graph(graph)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    load_project_settings()

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    do_config({'__file__': config_uri}, **settings)

    create_graph()

    # populate application models
    # for app in enabled_apps:
    #     app_name = app.APP_NAME
    #     app_module = importlib.import_module("apps.%s.scripts.populate" % app_name)
    #     #print("App Module: %s\n" % app_module.__name__)
    #
    #     try:
    #         app_module.populate_app(engine, db)
    #     except Exception as exp:
    #         print(repr(exp))
