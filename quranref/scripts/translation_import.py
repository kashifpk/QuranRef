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
    Translation,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print(('usage: %s <config_uri> translation_name filename\n'
           '(examples:\n    "%s development.ini ur.maududi data/translations/ur.maududi.txt")' % (cmd, cmd))) 
    sys.exit(1)


def import_translation(translation_name, filename):
    file = open(filename)
    with transaction.manager:
        for line in file:
            if not line.strip():
                break
            
            surah, aya, content = line.split('|')
            new_rec = Translation(
                translation_name=translation_name,
                surah=surah,
                aya_number=aya,
                translation_text=content)
            db.add(new_rec)
    
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
    
    import_translation(sys.argv[2], sys.argv[3])
    

