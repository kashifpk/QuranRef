"""
Quran Models
============

Contains models for storing Quran Ayas, Arabic Texts, Translations, References etc
"""

import logging
import hashlib

from marshmallow import Schema
from marshmallow.fields import String, Date, Integer, Float, Boolean, DateTime, List, Dict
from arango_orm import Collection, Relation, Graph, GraphConnection

from .common import add_document_if_not_exists
from quranref.graph_models import gdb
# import pdb

log = logging.getLogger(__name__)


class Surah(Collection):
    "Surah related info"

    __collection__ = 'surahs'

    class _Schema(Schema):
        _key = String(required=True)  # the surah number
        arabic_name = String(required=True)
        english_name = String(required=True)
        translated_name = String(required=True)
        nuzool_location = String(required=True, options=['Meccan', 'Medinan'])
        nuzool_order = Integer(required=True)
        rukus = Integer(required=True)
        total_ayas = Integer(required=True)


class Aya(Collection):
    "Aya database representation"

    __collection__ = 'ayas'

    _index = [
        {"type": "hash", "fields": ["surah_aya_number"]}
    ]

    class _Schema(Schema):
        _key = String(required=True)  # the aya number (format: surah_number-aya_number

    @classmethod
    def new(cls, surah_number, aya_number):

        surah = gdb.query(Surah).by_key(str(surah_number))

        # Add aya
        aya = cls(
            _key="{}-{}".format(surah_number, aya_number)
        )
        add_document_if_not_exists(aya, return_document='never')
        # log.debug(aya.surah_aya_number)

        # add surah aya link
        has_key = "{}-{}".format(surah._key, aya._key)
        has_document = Graph().relation(surah, Has(_key=has_key), aya)
        add_document_if_not_exists(has_document, return_document='never')

        return aya


class Text(Collection):
    """
    Aya text in different languages like arabic, urdu, english, etc
    and forms like simple, uthmani, simple minimal, etc
    """

    __collection__ = 'texts'

    class _Schema(Schema):
        _key = String(required=True)  # sha1 hash of text
        text = String(required=True)

    @classmethod
    def new(cls, text):
        key = hashlib.sha1(text.encode("UTF-8")).hexdigest()
        return cls(_key=key, text=text)


class Has(Relation):

    __collection__ = 'has'

    class _Schema(Schema):
        _key = String(required=True)  # surah_number-aya-number


class AyaText(Relation):

    __collection__ = 'aya_texts'

    class _Schema(Schema):
        _key = String(required=True)  # aya_number-text_key
        language = String(required=True)
        text_type = String(required=True, options=['text', 'translation'])

    @classmethod
    def new(cls, aya, aya_text, language, text_type):

        # Add aya text
        text_doc = Text.new(aya_text)
        add_document_if_not_exists(text_doc, return_document='never')

        # Add aya text link
        aya_text_key = "{}-{}".format(aya._key, text_doc._key)
        aya_text_document = Graph().relation(
            aya,
            cls(_key=aya_text_key, language=language, text_type=text_type),
            text_doc
        )
        add_document_if_not_exists(aya_text_document, return_document='never')


class QuranGraph(Graph):

    __graph__ = 'quran_graph'

    graph_connections = [
        GraphConnection(Surah, Has, Aya),
        GraphConnection(Aya, AyaText, Text),
        # GraphConnection(Surah, Has, [Aya]),
    ]
