import os
import sys
import logging

from pyramid.paster import get_appsettings, setup_logging

from .. import load_project_settings, do_config

log = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print(('usage: %s <config_uri> arabic_text_name filename\n'
           '(examples:\n    "%s development.ini uthmani data/quran-uthmani.txt")' % (cmd, cmd)))
    sys.exit(1)


def import_ayas(text_name, filename):

    from ..graph_models.quran_graph import Aya, AyaText

    file = open(filename)

    for line in file:
        if not line.strip():
            break

        surah, aya, content = line.split('|')
        aya_doc = Aya.new(
            surah_number=surah,
            aya_number=aya
        )

        AyaText.new(aya_doc, content.strip(), 'arabic', text_name)

    log.info("Done importing!")


def main(argv=sys.argv):
    if len(argv) != 4:
        usage(argv)

    load_project_settings()

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    do_config({'__file__': config_uri}, **settings)

    import_ayas(sys.argv[2], sys.argv[3])
