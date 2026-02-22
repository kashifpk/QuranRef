"""
Quran Models

Contains models for storing Quran Ayas, Arabic Texts, Translations, References etc.
Uses Apache AGE graph database via age-orm.
"""

from typing import Literal

from age_orm import Edge, Graph, Vertex

from .utils import text_to_digest


class Surah(Vertex):
    "Surah related info"

    __label__ = "Surah"

    id: str  # surah number as string
    surah_number: int
    arabic_name: str
    english_name: str
    translated_name: str
    nuzool_location: Literal["Meccan", "Medinan"]
    nuzool_order: int
    rukus: int
    total_ayas: int


class Aya(Vertex):
    "Aya database representation"

    __label__ = "Aya"

    id: str  # format: "{surah_number}:{aya_number}"
    surah_key: str
    aya_number: int

    @classmethod
    def new(cls, graph: Graph, surah_number: int, aya_number: int) -> "Aya":
        aya_key = f"{surah_number}:{aya_number}"
        existing = graph.query(Aya).by_property("id", aya_key)
        if existing:
            return existing
        aya = cls(id=aya_key, surah_key=str(surah_number), aya_number=aya_number)
        graph.add(aya)
        return aya

    @classmethod
    def get_or_new(cls, graph: Graph, surah_number: int, aya_number: int) -> "Aya":
        aya_key = f"{surah_number}:{aya_number}"
        existing = graph.query(Aya).by_property("id", aya_key)
        if existing:
            return existing
        return cls.new(graph, surah_number, aya_number)


class Text(Vertex):
    "Stores deduplicated text content"

    __label__ = "Text"

    id: str  # SHA-256 digest of text
    text: str

    @classmethod
    def new(cls, graph: Graph, text: str) -> "Text":
        doc_key = text_to_digest(text)
        existing = graph.query(Text).by_property("id", doc_key)
        if existing:
            return existing
        doc = cls(id=doc_key, text=text)
        graph.add(doc)
        return doc


class Word(Vertex):
    "Represents a single word of the Quran"

    __label__ = "Word"

    id: str  # sha256 hash of word
    word: str
    count: int = 1

    @classmethod
    def new(cls, word: str, count: int = 1) -> "Word":
        word_hash = text_to_digest(word)
        return cls(id=word_hash, word=word, count=count)


class HasAya(Edge):
    "Links Surah to Aya"

    __label__ = "HAS_AYA"


class HasWord(Edge):
    "Links Aya to Word"

    __label__ = "HAS_WORD"


class AyaText(Edge):
    "Links Aya to Text with language and text_type metadata"

    __label__ = "AYA_TEXT"

    language: str
    text_type: str

    @classmethod
    def new(
        cls, graph: Graph, aya: Aya, aya_text: str, language: str, text_type: str
    ) -> "AyaText":
        text_doc = Text.new(graph, aya_text)
        edge = cls(language=language, text_type=text_type)
        graph.connect(aya, edge, text_doc)
        return edge
