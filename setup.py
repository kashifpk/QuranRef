import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    "PyCK",
    "pyramid",
    "pyramid_mako",
    "pyramid_debugtoolbar",
    "webtest",
    "waitress",
    "arango-orm",
    "python-jose",
]


setup(
    name="quranref",
    version="1.3",
    description="quranref",
    long_description="Online and Embeddable Quran Reference and Tafseer collection",
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="",
    author_email="",
    url="",
    keywords="web PyCK framework pylons pyramid",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite="quranref",
    install_requires=requires,
    entry_points="""\
    [paste.app_factory]
    main = quranref:main
    [console_scripts]
    quranref_populate = quranref.scripts.populate:main
    quranref_import_surah_info = quranref.scripts.surah_info_import:main
    quranref_import_text = quranref.scripts.text_import:main
    quranref_make_words = quranref.scripts.make_words:main
    """,
)
