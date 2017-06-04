import os
import sys
import logging

from pyramid.paster import get_appsettings, setup_logging

from .. import load_project_settings, do_config
from ..lib.surah_info import surah_info

log = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print(('usage: %s <config_uri>\n'
           '(examples:\n    "%s development.ini")' % (cmd, cmd)))
    sys.exit(1)


def import_surahs():
    from ..graph_models import gdb
    from ..graph_models.quran_graph import Surah

    surah_number = 1
    for s_info in surah_info:
        s = Surah(
            _key=str(surah_number),
            surah_number=surah_number,
            arabic_name=s_info['arabic_name'],
            english_name=s_info['english_name'],
            translated_name=s_info['translated_name'],
            nuzool_location=s_info['nuzool_location'],
            nuzool_order=s_info['nuzool_order'],
            rukus=s_info['rukus'],
            total_ayas=s_info['total_ayas']
        )

        gdb.add(s)

        surah_number += 1

    log.info("Done importing!")


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    load_project_settings()

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    do_config({'__file__': config_uri}, **settings)

    import_surahs()
