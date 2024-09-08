"""
Quran Models

Contains models for storing Quran Ayas, Arabic Texts, Translations, References etc
"""

import hashlib
from typing import Literal

from pydantic import Field
from arango_orm import Database, Collection, Relation, Graph, GraphConnection
from arango_orm.config import CollectionConfig, IndexSpec


class Surah(Collection):
    "Surah related info"

    __collection__ = "surahs"

    # surah _key is the surah number as string
    surah_number: int
    arabic_name: str
    english_name: str
    translated_name: str
    nuzool_location: Literal["Meccan", "Medinan"]
    nuzool_order: int
    rukus: int
    total_ayas: int


class Aya(Collection):
    "Aya database representation"

    __collection__ = "ayas"

    _collection_config = CollectionConfig(
        indexes=[
            IndexSpec(index_type="hash", fields=["_key"], unique=True, sparse=False),
        ]
    )

    key_: str = Field(..., alias="_key")
    aya_number: int

    @classmethod
    def new(cls, db: Database, surah_number: int, aya_number: int) -> "Aya":
        aya_key = f"{surah_number}-{aya_number}"
        aya = cls(key_=aya_key, aya_number=aya_number)
        aya: "Aya" = db.add(aya, if_present="ignore")

        has_document = Has(
            key_=aya_key,
            _from=f"{Surah.__collection__}/{surah_number}",
            _to=f"{cls.__collection__}/{aya_key}",
        )

        db.add(has_document, if_present="ignore")

        return aya


class Text(Collection):
    """
    Aya text in different languages like arabic, urdu, english, etc
    and forms like simple, uthmani, simple minimal, etc
    """

    __collection__ = "texts"

    # _key is sha1 hash of text
    text: str

    @classmethod
    def new(cls, db: Database, text: str) -> "Text":
        text_hash = hashlib.sha1(text.encode()).hexdigest()
        text_document = cls(key_=text_hash, text=text)
        text_document: "Text" = db.add(text_document, if_present="ignore")

        return text_document


class Has(Relation):
    __collection__ = "has"


class AyaText(Relation):
    "Linkage between Aya and various texts (arabic or translations)"

    __collection__ = "aya_texts"

    # _key is  f"{aya_key}-{text_key}-{language}-{text_type}
    language: str
    text_type: str

    @classmethod
    def new(cls, db: Database, aya: Aya, aya_text: str, language: str, text_type: str) -> "AyaText":
        # Add aya text
        text_doc = Text.new(db, aya_text)
        text_doc = db.add(text_doc, if_present="ignore")

        # Add aya text link
        aya_text_key = f"{aya._key}-{text_doc._key}-{language}-{text_type}"
        aya_text_doc = Graph().relation(
            aya, cls(key_=aya_text_key, language=language, text_type=text_type), text_doc
        )

        aya_text_doc: "AyaText" = db.add(aya_text, if_present="ignore")

        return aya_text_doc


class Word(Collection):
    "Represents a single word of the Quran"

    __collection__ = "words"

    _collection_config = CollectionConfig(
        indexes=[
            IndexSpec(index_type="skiplist", fields=["word"], unique=False, sparse=False),
            IndexSpec(index_type="skiplist", fields=["count"], unique=False, sparse=False),
        ]
    )

    key_: str = Field(..., alias="_key")  # sha1 hash of word
    word: str
    count: int | None = 1

    @classmethod
    def new(cls, db: Database, word: str, count=1) -> "Word":
        word_hash = hashlib.sha1(word.encode()).hexdigest()
        word_document = cls(key_=word_hash, word=word, count=count)
        word_document: "Word" = db.add(word_document, if_present="ignore")

        return word_document


class QuranGraph(Graph):
    __graph__ = "quran_graph"

    graph_connections = [
        GraphConnection([Surah, Aya], Has, [Aya, Word]),
        GraphConnection(Aya, AyaText, Text),
    ]
