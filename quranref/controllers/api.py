"""
QuranRef API
============

API access to the QuranRef site

GET /api/v1/surahs
__________________

Get surahs list

.. code-block:: shell

    curl -XGET -H "Content-Type: application/json" "http://api.threatify.com/api/surahs" 


GET /api/v1/letters
___________________

Get letters list from which Quranic words start

.. code-block:: shell

    curl -XGET -H "Content-Type: application/json" \\
         "http://api.threatify.com/api/letters" 


GET /api/v1/words_by_letter/{arabic_letter}
_____________________________________________

Get all words that start by the specified arabic letter.

.. code-block:: shell

    curl -XGET -H "Content-Type: application/json" \\
         "http://api.threatify.com/api/words_by_letter/ب" 


GET /api/v1/ayas_by_word/{arabic_word}/{languages}
__________________________________________________

Get all ayas containing the given word and return text in the given languages and
specific translator. Language items are separated by underscore while within a
language item there is the language name and it's text type/translation separated by
comma.

For example:
    arabic,simple means arabic content with simple syntax.
    urdu,maududi returns urdu translations by Maududi

.. code-block:: shell

    curl -XGET -H "Content-Type: application/json" \\
         "http://api.threatify.com/api/ayas_by_word/عابد/arabic,simple_urdu,maududi_english,maududi"


GET /api/v1/text_types
______________________

Get available languages and the text types/translations supported by them

.. code-block:: shell

    curl -XGET -H "Content-Type: application/json" \\
         "http://api.threatify.com/api/text_types"

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
            ('ayas_by_word/{word}/{languages}', 'get_ayas_by_word'),
            ('text_types', 'get_text_types'),
            ('qref/{surah}/{languages}', 'qref_text'),
            ('search/{search_term}/{languages}', 'do_search'),
            ('{occurrence}/common/{rec_count}', 'get_top_words'),
            ('words_by_count/{count}', 'words_by_count'),
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
        RETURN doc
        """.format(letter=self.endpoint_info['letter'])

        results = [(r['word'], r['count']) for r in self.gdb._db.aql.execute(aql)]

        return results

    def _process_aya_results(self, obj):  # pylint: disable=R0201
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

    def get_ayas_by_word(self):

        word_doc = self.gdb.query(Word).filter("word==@word", word=self.endpoint_info['word']).all()
        if not word_doc:
            return []

        word_doc = word_doc[0]

        aql = "FOR v, e, p IN 1..2 ANY 'words/{wkey}' GRAPH 'quran_graph'\n".format(
            wkey=word_doc._key
        )

        aql += 'FILTER '
        for lang in self.endpoint_info['languages'].split('_'):
            language, text_type = lang.split(',')

            aql += '(e.language=="{language}" && e.text_type=="{text_type}") OR '.format(
                language=language, text_type=text_type
            )

        aql = aql.strip(' OR ')  # pylint: disable=E1310
        aql += "\nRETURN p"

        log.debug(aql)
        obj = self.qgraph.aql(aql)
        if not obj:
            return []

        # log.debug(obj._relations)
        return self._process_aya_results(obj)

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
        return self._process_aya_results(obj)

    def do_search(self):

        aarab = ['ِ', 'ْ', 'َ', 'ُ', 'ّ', 'ٍ', 'ً', 'ٌ']

        search_results = []
        search_term = ''
        # is_plain = True
        # for ch in aarab:
        #     if ch in search_term:
        #         is_plain = False
        #         break
        for ch in self.endpoint_info['search_term']:
            if ch not in aarab:
                search_term += ch

        if search_term:
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

                log.debug(aql)
                obj = self.qgraph.aql(aql)
                if not obj:
                    continue

                # log.debug(obj)
                log.debug(obj._dump())
                log.debug(obj._relations)
                # log.info(obj._relations['aya_texts'][0]._next._key)
                for aya_text_doc in obj._relations['aya_texts']:
                    search_result = {
                        'aya_number': aya_text_doc._next._key,
                        'texts': {'arabic': {'simple-clean': mt.text}}
                    }
                    log.debug(search_result)

                    languages = self.endpoint_info['languages'].split('_')
                    if len(languages) == 1 and languages[0] == 'arabic,simple-clean':
                        search_results.append(search_result)
                        continue

                    log.info(languages)
                    aql = "FOR v, e, p IN 1..2 OUTBOUND 'ayas/{}' GRAPH 'quran_graph'\n".format(
                        search_result['aya_number']
                    )

                    aql += 'FILTER '
                    for lang in self.endpoint_info['languages'].split('_'):
                        language, text_type = lang.split(',')

                        aql += '(e.language=="{language}" && e.text_type=="{text_type}") OR '.format(
                            language=language, text_type=text_type
                        )

                    aql = aql.strip(' OR ')  # pylint: disable=E1310
                    aql += "\nRETURN p"
                    log.info(aql)

                    # get arabic text of the specified style
                    # aql = """
                    # FOR v, e, p IN 1..2 OUTBOUND 'ayas/{}' GRAPH 'quran_graph'
                    #     FILTER p.edges[0].text_type=="{}"
                    # RETURN p
                    # """.format(search_result['aya_number'], result_text_type)

                    aya_obj = self.qgraph.aql(aql)
                    # search_result['texts']['arabic'][result_text_type] = \
                    #     aya_obj._relations['aya_texts'][0]._next.text

                    for aya_text in aya_obj._relations['aya_texts']:
                        if aya_text.language not in search_result['texts']:
                            search_result['texts'][aya_text.language] = {}

                        search_result['texts'][aya_text.language][aya_text.text_type] = \
                            aya_text._next.text

                    search_results.append(search_result)

        return search_results

    def get_top_words(self):

        # {occurrence}/common/{rec_count}
        o_type = self.endpoint_info['occurrence']
        assert o_type in ['most', 'least']
        rec_count = int(self.endpoint_info['rec_count'])

        sort_str = ''
        if 'most' == o_type:
            sort_str = 'count DESC'
        else:
            sort_str = 'count'

        words = self.gdb.query(Word).sort(sort_str).sort('word').limit(rec_count).all()
        results = [(r.word, r.count) for r in words]

        return results

    def words_by_count(self):
        wc = int(self.endpoint_info['count'])
        words = self.gdb.query(Word).filter_by(count=wc).sort("word").all()
        results = [(r.word, r.count) for r in words]

        return results
