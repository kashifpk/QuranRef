"""
Quran Models

Contains models for storing Quran Ayas, Arabic Texts, Translations, References etc
"""

from typing import Literal, Any

from pydantic import Field
# from pydantic.json_schema import SkipJsonSchema
from arango_orm import Database, Collection, Relation, Graph, GraphConnection
# from arango_orm.references import Relationship, relationship
from arango_orm.config import CollectionConfig, IndexSpec
from arango_orm.exceptions import DocumentNotFoundError

from .utils import text_to_digest


class MetaInfo(Collection):
    "Meta information about the data present in the db"

    __collection__ = "meta_info"

    key_: str = Field(..., alias="_key")
    value: Any


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

    # ayas: SkipJsonSchema[list["Aya"]] = relationship(__name__ + ".Aya", "key_", target_field="surah_key")


class Aya(Collection):
    "Aya database representation"

    __collection__ = "ayas"

    _collection_config = CollectionConfig(
        indexes=[
            IndexSpec(index_type="hash", fields=["_key"], unique=True, sparse=False),
        ]
    )

    key_: str = Field(..., alias="_key")
    surah_key: str
    aya_number: int

    # surah: Surah = relationship(Surah, "surah_key")

    @classmethod
    def new(cls, db: Database, surah_number: int, aya_number: int) -> "Aya":
        aya_key = f"{surah_number}:{aya_number}"
        aya = cls(key_=aya_key, surah_key=str(surah_number), aya_number=aya_number)
        aya: "Aya" = db.add(aya, if_present="ignore")

        return aya

    @classmethod
    def get_or_new(cls, db: Database, surah_number: int, aya_number: int) -> "Aya":
        aya_key = f"{surah_number}:{aya_number}"
        try:
            aya = db.query(Aya).by_key(aya_key)
        except DocumentNotFoundError:
            aya = cls.new(db, surah_number, aya_number)

        return aya


class Text(Collection):
    "Linkage between Aya and various translations"

    __collection__ = "texts"

    # _key is  f"{aya_key}-{text_key}-{language}-{text_type}
    # key is hash diget of text
    text: str

    @classmethod
    def new(cls, db: Database, text: str) -> "Text":
        # Add aya text
        doc_key = text_to_digest(text)
        doc = cls(key_=doc_key, text=text)
        db.add(doc, if_present="ignore")

        return doc


class Has(Relation):
    __collection__ = "has"


class AyaText(Relation):
    "Linkage between Aya and various texts and translations"

    __collection__ = "aya_texts"

    # Key is aya_number-text_key-language-text-type
    language: str
    text_type: str

    @classmethod
    def new(cls, db: Database, aya: Aya, aya_text: str, language: str, text_type: str) -> "AyaText":
        text_doc = Text.new(db, aya_text)

        aya_text_key = f"{aya.key_}:{text_doc.key_}:{language}:{text_type}"
        aya_text_doc = Graph().relation(
            aya, cls(key_=aya_text_key, language=language, text_type=text_type), text_doc
        )
        aya_text_doc: "AyaText" = db.add(aya_text_doc, if_present="ignore")

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
        word_hash = text_to_digest(word)
        word_document = cls(key_=word_hash, word=word, count=count)
        # word_document: "Word" = db.add(word_document, if_present="ignore")

        return word_document


class QuranGraph(Graph):
    __graph__ = "quran_graph"

    graph_connections: list[GraphConnection] = [
        GraphConnection([Surah, Aya], Has, [Aya, Word]),
        GraphConnection(Aya, AyaText, Text)
    ]
