import os
from pyramid.paster import get_app, setup_logging

here = os.path.dirname(os.path.realpath(__file__))
ini_path = here + '/quranref.ini'
setup_logging(ini_path)
application = get_app(ini_path, 'main')
