"""
QuranRef API
============

API access to the QuranRef site

GET /api/v1/assets
__________________

Return a list of all assets of the current user. Requires user's auth token in request headers.

Example::

    curl "http://api.threatify.com/api/v1/assets" -H "Content-Type: application/json"

Returns something like::

    [
        {
            "_id": "domains/www.threatify.com",
            "verified": true,
            "value": "www.threatify.com",
            "_relations": [
                  {"has_ip": "ip_addresses/122.122.122.122"}
             ]
        },
        {
            "_id": "ip_addresses/122.122.122.122",
            "verified": false,
            "value": "122.122.122.122"
        }
    ]


GET /api/v1/assets/{asset_id}
_____________________________

Return details of given asset. Please note that asset ID is of the form
**domains/www.threatify.com**. Supports the query string parameter depth. Depth specifies how
much information is required. Default is 1 which also returns all relations and their
information. All linked documents are placed inside the _relations key.

Example::

    curl -XGET "http://api.threatify.com/api/v1/assets/domains/www.threatify.com -H "Content-Type: application/json"

Returns something like::


    {
        "_id": "domains/www.threatify.com",
        "verified": true,
        "value": "www.threatify.com",
        "_relations": [
            {
                "has_ip": {
                    "_id": "ip_addresses/122.122.122.122",
                    "verified": false,
                    "value": "122.122.122.122"
                }
            }
         ]
    }

POST /api/v1/assets
___________________

Creates a new asset for the user. Assets that the user adds using this API are automatically
marked as verified. Requires user's auth token in request headers. Requires the following info in
POST's JSON data:

* **asset_type**: Currently can be either **domain** or **ip**
* **value**: The actual domain or ip address of the asset.

Example::

    curl -XPOST "http://api.threatify.com/api/v1/assets" -H "Content-Type: application/json" \\
    -X POST -d '{"asset_type": "domain", "value": "threatify.com"}'

Returns::

    {"msg": "ok", "_id": "domains/threatify.com"}


"""

import logging

from pyramid.view import view_defaults, view_config
from .api_base import APIBase
from . import GraphMixin
from .exceptions import APIForbidden, APIBadRequest, APITooManyRequests

from ..graph_models.quran_graph import QuranGraph, Surah, Aya, Text, Word
from .. import graph_models

log = logging.getLogger(__name__)


@view_defaults(route_name='api', renderer="prettyjson")
class QrefAPI(APIBase, GraphMixin):

    _ENDPOINTS = {
        'GET': [
            ('surahs', 'surah_list'),
            ('letters', 'letters'),
            ('words_by_letter/{letter}', 'get_words_by_letter'),
            ('ayas_by_word/{word}/{result_text_type}', 'get_ayas_by_word'),
            ('text_types', 'get_text_types'),
            ('qref/{surah}/{languages}', 'qref_text'),
            ('search/{search_term}/{result_text_type}', 'do_search')
        ],
        # 'POST': [
        #     ('', 'new_asset')
        # ]
    }

    def __init__(self, request):
        APIBase.__init__(self, request)
        GraphMixin.__init__(self)

    @view_config(request_method=("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"))
    def request_handler(self):
        return self.handle_request()

    def letters(self):  # pylint: disable=R0201
        letters_list = [
            "آ", "أ", "إ", "ا", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش",
            "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "و", "ه", "ي"
        ]

        return letters_list

    def get_words_by_letter(self):

        aql = """
        FOR doc IN words
            FILTER LEFT(doc.word, 1)=='{letter}'
            SORT doc.word
        RETURN doc.word
        """.format(letter=self.endpoint_info['letter'])

        results = [r for r in self.gdb._db.aql.execute(aql)]
        # log.debug(results)

        return results

    def get_ayas_by_word(self):

        word_doc = self.gdb.query(Word).filter("word==@word", word=self.endpoint_info['word']).all()
        if not word_doc:
            return []

        word_doc = word_doc[0]
        r_text_type = self.endpoint_info['result_text_type']

        aql = """
        FOR v, e, p IN 1..2 ANY 'words/{wkey}' GRAPH 'quran_graph'
            FILTER p.edges[1].text_type=="{text_type}"
                AND p.edges[1].language=="arabic"
        RETURN p
        """.format(wkey=word_doc._key, text_type=r_text_type)

        obj = self.qgraph.aql(aql)
        if not obj:
            return []

        # log.debug(obj._relations)

        results = []
        ayas = [r._next for r in obj._relations['has']]
        for aya in ayas:
            # log.debug(aya._relations)
            r = {
                'aya_number': aya._key,
                'texts': {'arabic': {r_text_type: aya._relations['aya_texts'][0]._next.text}}
            }

            results.append(r)

        return results

    def surah_list(self):

        surahs = self.gdb.query(Surah).sort("surah_number").all()
        results = {}
        for surah in surahs:
            results[surah._key] = surah._dump()

        return results

    def get_text_types(self):

        aql = """
        FOR doc IN aya_texts
        RETURN DISTINCT {language: doc.language, text_type: doc.text_type}
        """

        results = [r for r in self.gdb._db.aql.execute(aql)]
        # log.debug(results)
        final_results = {}
        for d in results:
            if d['language'] not in final_results:
                final_results[d['language']] = []

            final_results[d['language']].append(d['text_type'])

        return final_results

    def qref_text(self):
        """
        Return quran text for request surah and optionally aya(s) in request language(s) and
        text type(s)

        qref/{surah}/{language1,text_type_1}...
        qref/1/arabic,uthmani
        qref/1,0-3/arabic,uthmani_urdu,maududi_english,maududi

        """

        # log.debug(self.gdb)
        # log.debug(self.qgraph)
        surah = self.endpoint_info['surah']
        aya = None
        if ',' in surah:
            surah, aya = surah.split(',')

        languages = self.endpoint_info['languages']
        # log.info(surah)
        # log.info(languages)

        aql = "FOR v, e, p IN 1..2 OUTBOUND 'surahs/{surah}' GRAPH 'quran_graph'\n".format(
            surah=surah)

        # Add aya filter
        if aya is not None:
            if '-' not in aya:
                aql += "FILTER p['vertices'][1].aya_number=={}\n".format(aya)
            else:
                start_aya, end_aya = aya.split('-')

                aql += "FILTER p['vertices'][1].aya_number>={} ".format(start_aya) + \
                    "AND p['vertices'][1].aya_number<={}\n".format(end_aya)

        # Add language and text_type filters
        aql += 'FILTER '
        for lang in languages.split('_'):
            language, text_type = lang.split(',')

            aql += '(e.language=="{language}" && e.text_type=="{text_type}") OR '.format(
                language=language, text_type=text_type
            )

        aql = aql.strip(' OR ')
        aql += "\nSORT p['vertices'][1].aya_number\nRETURN p"
        # log.debug(aql)

        obj = self.qgraph.aql(aql)
        # log.debug(obj._relations)
        ayas = []
        for rel in obj._relations['has']:
            # log.info(rel._next._relations['aya_texts'])

            d = {'aya_number': rel._next.aya_number, 'aya': rel._next._key, 'texts': {}}
            for aya_text in rel._next._relations['aya_texts']:
                if aya_text.language not in d['texts']:
                    d['texts'][aya_text.language] = {}

                d['texts'][aya_text.language][aya_text.text_type] = aya_text._next.text

            ayas.append(d)

        return ayas

    def do_search(self):

        aarab = ['ِ', 'ْ', 'َ', 'ُ', 'ّ', 'ٍ', 'ً', 'ٌ']

        search_results = []
        search_term = self.endpoint_info['search_term']
        result_text_type = self.endpoint_info['result_text_type']
        is_plain = True
        for ch in aarab:
            if ch in search_term:
                is_plain = False
                break

        if is_plain:
            matched_texts = self.gdb.query(Text).filter(
                "LIKE(rec.text, '%{}%')".format(search_term), prepend_rec_name=False).all()

            # search_results = [rec.text for rec in matched_texts]
            # log.debug(matched_texts)

            for mt in matched_texts:
                aql = """
                FOR v, e, p IN 1..1 INBOUND 'texts/{}' GRAPH 'quran_graph'
                    FILTER p.edges[0].text_type=="simple-clean"
                        AND p.edges[0].language=="arabic"
                RETURN p""".format(mt._key)

                # log.debug(aql)
                obj = self.qgraph.aql(aql)
                if not obj:
                    continue

                # log.debug(obj)
                # log.debug(obj._dump())
                # log.debug(obj._relations)
                # log.info(obj._relations['aya_texts'][0]._next._key)
                for aya_text_doc in obj._relations['aya_texts']:
                    search_result = {
                        'aya_number': aya_text_doc._next._key,
                        'texts': {'arabic': {'simple-clean': mt.text}}
                    }

                    if 'simple-clean' != result_text_type:
                        # get arabic text of the specified style
                        aql = """
                        FOR v, e, p IN 1..2 OUTBOUND 'ayas/{}' GRAPH 'quran_graph'
                            FILTER p.edges[0].text_type=="{}"
                        RETURN p
                        """.format(search_result['aya_number'], result_text_type)

                        aya_obj = self.qgraph.aql(aql)
                        search_result['texts']['arabic'][result_text_type] = \
                            aya_obj._relations['aya_texts'][0]._next.text

                    search_results.append(search_result)

        return search_results
