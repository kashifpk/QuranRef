import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from .. import load_project_settings

import logging
log = logging.getLogger(__name__)

from ..models import (
    db,
    Aya,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print(('usage: %s <config_uri> import_type filename\n'
           '(examples:\n    "%s development.ini ayas data/quran-uthmani.txt")' % (cmd, cmd))) 
    sys.exit(1)


def import_ayas(filename):
    file = open(filename)
    with transaction.manager:
        for line in file:
            if not line.strip():
                break
            
            surah, aya, content = line.split('|')
            new_aya = Aya(surah=surah,
                          aya_number=aya,
                          arabic_text=content)
            db.add(new_aya)
    
    log.info("Done importing!")
    

def main(argv=sys.argv):
    if len(argv) != 4:
        usage(argv)

    load_project_settings()

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    db.configure(bind=engine)
    db.autoflush = True
    
    if 'ayas' == sys.argv[2]:
        import_ayas(sys.argv[3])
    

