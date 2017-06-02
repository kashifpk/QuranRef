"""
Quran Models
============

Contains models for storing Quran Ayas, Arabic Texts, Translations, References etc
"""

import logging

from marshmallow import Schema
from marshmallow.fields import String, Date, Integer, Float, Boolean, DateTime, List, Dict
from arango_orm import Collection, Relation, Graph, GraphConnection


from .common import add_document_if_not_exists, update_document

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
        _key = String(required=True)  # the aya number
        surah_aya_number = String()   # (format: surah_number-aya_number


class Text(Collection):
    """
    Aya text in different languages like arabic, urdu, english, etc
    and forms like simple, uthmani, simple minimal, etc
    """

    __collection__ = 'texts'

    class _Schema(Schema):
        _key = String(required=True)  # auto value
        text = String(required=True)


class Has(Relation):

    __collection__ = 'has'

    class _Schema(Schema):
        _key = String(required=True)


class AyaText(Relation):

    __collection__ = 'aya_texts'

    class _Schema(Schema):
        _key = String(required=True)
        language = String(required=True)
        text_type = String(required=True, options=['text', 'translation'])


class QuranGraph(Graph):

    __graph__ = 'quran_graph'

    graph_connections = [
        GraphConnection(Surah, Has, Aya),
        GraphConnection(Aya, AyaText, Text),
        # GraphConnection(Surah, Has, [Aya]),
    ]
