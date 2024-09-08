"""
Quran Models

Contains models for storing Quran Ayas, Arabic Texts, Translations, References etc
"""

from typing import Literal

from pydantic import Field, BaseModel
from arango_orm import Database, Collection, Relation, Graph, GraphConnection
from arango_orm.references import relationship
from arango_orm.config import CollectionConfig, IndexSpec

from .utils import text_to_digest


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

    ayas: list["Aya"] = relationship(__name__ + ".Aya", "key_", target_field="surah")


class AyaText(BaseModel):
    "Arabic text representation of a single aya"

    text_type: Literal[
        "simple", "simple-minimal", "simple-clean", "simple-plain", "uthmani", "uthmani-minimal"
    ]
    text: str


class Aya(Collection):
    "Aya database representation"

    __collection__ = "ayas"

    _collection_config = CollectionConfig(
        indexes=[
            IndexSpec(index_type="hash", fields=["_key"], unique=True, sparse=False),
        ]
    )

    key_: str = Field(..., alias="_key")
    surah: str
    aya_number: int
    texts: list[AyaText] = []

    surah: Surah = relationship(Surah, "surah")
    translations: list["Translation"] = relationship(__name__ + ".Translation", "key_", target_field="aya")

    @classmethod
    def new(cls, db: Database, surah_number: int, aya_number: int) -> "Aya":
        aya_key = f"{surah_number}-{aya_number}"
        aya = cls(key_=aya_key, aya_number=aya_number)
        aya: "Aya" = db.add(aya, if_present="ignore")

        return aya


class Translation(Relation):
    "Linkage between Aya and various translations"

    __collection__ = "translations"

    # _key is  f"{aya_key}-{text_key}-{language}-{text_type}
    aya: str
    language: str
    translation: str
    text: str

    aya: Aya = relationship(Aya, "aya")

    @classmethod
    def new(cls, db: Database, aya: Aya, language: str, translation: str, text: str) -> "AyaText":
        # Add aya text
        doc_key = text_to_digest(aya.key_ + language + translation + text)
        doc = cls(key_=doc_key, aya=aya.key_, language=language, translation=translation, text=text)
        doc: "Translation" = db.add(doc, if_present="ignore")

        return doc


class Has(Relation):
    __collection__ = "has"


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
        word_document: "Word" = db.add(word_document, if_present="ignore")

        return word_document


class QuranGraph(Graph):
    __graph__ = "quran_graph"

    graph_connections: list[GraphConnection] = [
        GraphConnection(Aya, Has, Word)
    ]
