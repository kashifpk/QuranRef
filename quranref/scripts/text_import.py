"""
Import Quran Text in different languages and types
Examples:
Language: arabic, text_type: uthmani
Language: urdu, text_type: maududi
"""

import os
import sys
import logging

from pyramid.paster import get_appsettings, setup_logging

from .. import load_project_settings, do_config

log = logging.getLogger(__name__)


def usage(argv):
    cmd = os.path.basename(argv[0])
    help_msg = """
    Usage: {prog} <config_uri> language text_type filename
    Examples:
        {prog} development.ini arabic uthmani data/quran-uthmani.txt
        {prog} development.ini urdu maududi data/translations/ur.maududi.txt
    """.format(prog=cmd)
    print(help_msg)
    sys.exit(1)


def import_text(language, text_name, filename):

    from ..graph_models.quran_graph import Aya, AyaText

    file = open(filename)

    bismillah_text = ''
    current_surah = ''

    for line in file:
        if not line.strip():
            break

        surah, aya, content = line.split('|')

        if not bismillah_text:
            bismillah_text = content.strip()

        if current_surah != surah and content.startswith(bismillah_text):
            # new surah starting, separate bismillah and save as aya 0 for surah
            content = content[len(bismillah_text):].strip()
            if content:
                aya_doc = Aya.new(surah_number=surah, aya_number=0)
            else:
                aya_doc = Aya.new(surah_number=surah, aya_number=aya)

            AyaText.new(aya_doc, bismillah_text, language, text_name)
            current_surah = surah

        if content:
            aya_doc = Aya.new(surah_number=surah, aya_number=aya)
            AyaText.new(aya_doc, content.strip(), language, text_name)

    log.info("Done importing!")


def main(argv=sys.argv):  # pylint: disable=W0102
    if len(argv) != 5:
        usage(argv)

    load_project_settings()

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    do_config({'__file__': config_uri}, **settings)

    import_text(sys.argv[2], sys.argv[3], sys.argv[4])
