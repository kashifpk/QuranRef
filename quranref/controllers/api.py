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
from .exceptions import APIForbidden, APIBadRequest, APITooManyRequests

from ..graph_models.quran_graph import QuranGraph, Surah, Aya, Text, Word
from .. import graph_models

log = logging.getLogger(__name__)


@view_defaults(route_name='api', renderer="prettyjson")
class QrefAPI(APIBase):

    _ENDPOINTS = {
        'GET': [
            ('surahs', 'surah_list'),
            ('letters', 'letters'),
            ('words_by_letter/{letter}', 'get_words_by_letter'),
            ('ayas_by_word/{word}/{result_text_type}', 'get_ayas_by_word'),
            ('text_types', 'get_text_types'),
            ('qref/{text_type}/{surah}', 'qref_arabic_text'),
            ('qref/{text_type}/{surah}/{aya}', 'qref_arabic_text'),
            ('search/{search_term}/{result_text_type}', 'do_search')
        ],
        # 'POST': [
        #     ('', 'new_asset')
        # ]
    }

    @view_config(request_method=("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"))
    def request_handler(self):
        return self.handle_request()

    def letters(self):
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

        gdb = graph_models.gdb
        results = [r for r in gdb._db.aql.execute(aql)]
        # log.debug(results)

        return results

    def get_ayas_by_word(self):

        gdb = graph_models.gdb
        qgraph = QuranGraph(connection=gdb)

        word_doc = gdb.query(Word).filter("word==@word", word=self.endpoint_info['word']).all()
        if not word_doc:
            return []

        word_doc = word_doc[0]

        aql = """
        FOR v, e, p IN 1..2 ANY 'words/{wkey}' GRAPH 'quran_graph'
            FILTER p.edges[1].text_type=="{text_type}"
        RETURN p
        """.format(wkey=word_doc._key, text_type=self.endpoint_info['result_text_type'])

        obj = qgraph.aql(aql)
        if not obj:
            return []

        # log.debug(obj._relations)

        results = []
        ayas = [r._next for r in obj._relations['has']]
        for aya in ayas:
            r = {
                'aya_number': aya._key,
                'aya_text': aya._relations['aya_texts'][0]._next.text
            }

            qgraph.expand(aya)
            # log.info(aya._relations)
            for rel in aya._relations['has']:
                # log.debug(rel._next)
                surah = rel._next
                if not surah._id.startswith('surah'):
                    continue

                r['surah_arabic_name'] = surah.arabic_name
                r['surah_english_name'] = surah.english_name

            results.append(r)

        return results

    def surah_list(self):
        gdb = graph_models.gdb
        surahs = gdb.query(Surah).sort("surah_number").all()
        # log.debug(surahs)

        return [s._dump() for s in surahs]

    def get_text_types(self):

        aql = """
        FOR doc IN aya_texts
            FILTER doc.language=='arabic'
        RETURN DISTINCT doc.text_type
        """

        gdb = graph_models.gdb
        results = [r for r in gdb._db.aql.execute(aql)]
        # log.debug(results)

        return sorted(results)

    def qref_arabic_text(self):
        surah = self.endpoint_info['surah']
        text_type = self.endpoint_info['text_type']
        aya = self.endpoint_info.get('aya', None)

        gdb = graph_models.gdb
        surah_doc = gdb.query(Surah).by_key(surah)

        assert surah_doc is not None

        qgraph = QuranGraph(connection=gdb)

        # qgraph.expand(surah_doc, depth=2)
        # log.debug(surah_doc._relations['has'][1]._next._relations)

        aql = """
        FOR v, e, p IN 1..2 OUTBOUND 'surahs/{surah}' GRAPH 'quran_graph'
            FILTER e.text_type=="{text_type}"
            SORT p['vertices'][1].aya_number
        RETURN p
        """.format(surah=surah, text_type=text_type)

        obj = qgraph.aql(aql)
        # log.debug(obj)
        # log.debug(obj._dump())
        # log.debug(obj._relations)
        ayas_arabic = [dict(aya_text=rel._next._relations['aya_texts'][0]._next.text,
                            aya_number=rel._next.aya_number)
                       for rel in obj._relations['has']]
        # log.debug(ayas_arabic)

        # log.debug(obj._relations['has'][1]._next._relations['aya_texts'][0]._next.text)

        ret_dict = surah_doc._dump()
        ret_dict['ayas'] = ayas_arabic

        return ret_dict

    def do_search(self):

        gdb = graph_models.gdb
        qgraph = QuranGraph(connection=gdb)

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
            matched_texts = gdb.query(Text).filter(
                "LIKE(rec.text, '%{}%')".format(search_term), prepend_rec_name=False).all()

            # search_results = [rec.text for rec in matched_texts]

            for mt in matched_texts:
                aql = """
                FOR v, e, p IN 1..3 INBOUND 'texts/{}' GRAPH 'quran_graph'
                    FILTER p.edges[0].text_type=="simple-clean"
                RETURN p""".format(mt._key)

                obj = qgraph.aql(aql)
                if not obj:
                    return []

                # log.debug(obj)
                # log.debug(obj._dump())
                # log.debug(obj._relations)
                # log.info(obj._relations['aya_texts'][0]._next._key)
                for aya_text_doc in obj._relations['aya_texts']:
                    search_result = {
                        'surah': aya_text_doc._next._relations['has'][0]._next._dump(),
                        'aya_number': aya_text_doc._next._key,
                        'texts': {
                            'simple-clean': mt.text
                        }
                    }

                    if 'simple-clean' != result_text_type:
                        # get arabic text of the specified style
                        aql = """
                        FOR v, e, p IN 1..2 OUTBOUND 'ayas/{}' GRAPH 'quran_graph'
                            FILTER p.edges[0].text_type=="{}"
                        RETURN p
                        """.format(search_result['aya_number'], result_text_type)

                        aya_obj = qgraph.aql(aql)
                        search_result['texts'][result_text_type] = \
                            aya_obj._relations['aya_texts'][0]._next.text

                    search_results.append(search_result)

        return search_results
