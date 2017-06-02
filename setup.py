import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'PyCK',
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_mako',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'webtest',
    'waitress',
    'wtforms',
    'wtdojo',
    'psycopg2',
    'arango-orm'
]

if sys.version_info[:3] < (2, 5, 0):
    requires.append('pysqlite')

# Requires from subapps
from quranref.apps import enabled_apps
for enabled_app in enabled_apps:
    if hasattr(enabled_app, 'app_requires'):
        for requirement in enabled_app.app_requires:
            if requirement not in requires:
                requires.append(requirement)

setup(
    name='quranref',
    version='0.1',
    description='quranref',
    long_description='Online and Embeddable Quran Reference and Tafseer collection',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web PyCK framework pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='quranref',
    install_requires=requires,
    entry_points="""\
    [paste.app_factory]
    main = quranref:main
    [console_scripts]
    quranref_populate = quranref.scripts.populate:main
    quranref_newapp = quranref.scripts.newapp:main
    quranref_import_surah_info = quranref.scripts.surah_info_import:main
    quranref_import_arabic = quranref.scripts.arabic_import:main
    quranref_import_translation = quranref.scripts.translation_import:main
    """,
)
