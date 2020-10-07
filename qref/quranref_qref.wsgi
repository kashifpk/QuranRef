import os
import configparser

from bottle import get, request, static_file, error, view, default_app
from quranref import graph_models
from quranref.graph_models.quran_graph import QuranGraph, Surah

# Change working directory so relative paths (and template lookup) work again
here = os.path.dirname(__file__)
os.chdir(here)

# ... build or import your bottle application here ...


def to_arabic_num(s_in, reverse=True):
    arabic_digits = {
        '0': '٠',
        '1': '١',
        '2': '٢',
        '3': '٣',
        '4': '٤',
        '5': '٥',
        '6': '٦',
        '7': '٧',
        '8': '٨',
        '9': '٩'
    }

    ret = ''
    for d in s_in:
        ret += arabic_digits[d]

    if reverse:
        ret = ret[::-1]

    return ret


def get_db():
    if graph_models.gdb is None:
        config_path = os.path.join(here, 'quranref_api.ini')
        config = configparser.ConfigParser()
        config.read(config_path)

        graph_models.connect(
            server=config['app:main']['gdb.server'],
            port=config['app:main']['gdb.port'],
            username=config['app:main']['gdb.username'],
            password=config['app:main']['gdb.password'],
            db_name=config['app:main']['gdb.database']
        )

    return graph_models.gdb


def _process_aya_results(obj):
    ayas = []
    for rel in obj._relations['has']:
        # log.info(rel._next._relations['aya_texts'])

        d = {'aya_number': rel._next._key, 'texts': {}}
        for aya_text in rel._next._relations['aya_texts']:
            if aya_text.language not in d['texts']:
                d['texts'][aya_text.language] = {}

            d['texts'][aya_text.language][aya_text.text_type] = aya_text._next.text

        ayas.append(d)

    return ayas


@error(404)
@error(500)
def error404(error):
    return 'Invalid reference spec!'


@get('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root=os.path.join(here, 'static'))


@get('/<spec>')
@view('index')
def index(spec):
    """
    Return quran text for requested surah and aya(s) in requested language(s) and
    text type(s)

    qref/{surah}:[{ayas}][?params]
    qref/1
    qref/1:3
    qref/1:1-7
    qref/1:1-7?ar_tt=simple&ur=maududi&en=maududi
    """
    ar_tt = request.query.ar_tt or 'uthmani'  # pylint: disable=no-member

    parts = spec.split(':')
    surah = parts[0]
    aya = None
    if len(parts) > 1:
        aya = parts[1]

    # page = request.query.page or '1'
    # return f"Surah {surah}, ayas {ayas}"
    gdb = get_db()
    arabic_name = gdb.query(Surah).by_key(surah).arabic_name
    qgraph = QuranGraph.get_graph_instance(gdb)

    # languages = self.endpoint_info['languages']
    # log.info(surah)
    # log.info(languages)

    aql = f"FOR v, e, p IN 1..2 OUTBOUND 'surahs/{surah}' GRAPH 'quran_graph'\n"

    # Add aya filter
    if aya is not None:
        if '-' not in aya:
            aql += "FILTER p['vertices'][1].aya_number=={}\n".format(aya)
        else:
            start_aya, end_aya = aya.split('-')

            aql += "FILTER p['vertices'][1].aya_number>={} ".format(start_aya) + \
                "AND p['vertices'][1].aya_number<={}\n".format(end_aya)

    # Add language and text_type filters
    aql += f'FILTER (e.language=="arabic" && e.text_type=="{ar_tt}")'

    translations = []
    if request.query.ur:  # pylint: disable=no-member
        translations.append(['urdu', request.query.ur])  # pylint: disable=no-member
        # aql += f' OR (e.language=="{language}" && e.text_type=="{text_type}")'

    if request.query.en:  # pylint: disable=no-member
        translations.append(['english', request.query.en])  # pylint: disable=no-member

    for translation in translations:
        language, text_type = translation
        aql += f' OR (e.language=="{language}" && e.text_type=="{text_type}")'

    aql += "\nSORT p['vertices'][1].aya_number\nRETURN p"
    # log.debug(aql)

    obj = qgraph.aql(aql)
    # log.debug(obj._relations)
    return dict(
        surah=surah,
        arabic_name=arabic_name,
        aya_spec=aya,
        ayas=_process_aya_results(obj),
        ar_tt=ar_tt,
        to_arabic_num=to_arabic_num,
        translations=translations
    )


# Do NOT use bottle.run() with mod_wsgi
application = default_app()
