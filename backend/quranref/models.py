"""
Quran Models

Contains models for storing Quran Ayas, Arabic Texts, Translations, References etc.
Uses Apache AGE graph database via age-orm.
"""

from typing import Literal

from age_orm import Edge, Graph, Vertex
from pydantic import Field

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
    # Mushaf structure (set by `qul import-metadata`)
    juz: int | None = None
    hizb: int | None = None
    rub: int | None = None
    manzil: int | None = None
    ruku: int | None = None
    surah_ruku: int | None = None
    sajda: str | None = None  # "required" or "optional"

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
    def new(cls, graph: Graph, aya: Aya, aya_text: str, language: str, text_type: str) -> "AyaText":
        text_doc = Text.new(graph, aya_text)
        edge = cls(language=language, text_type=text_type)
        graph.connect(aya, edge, text_doc)
        return edge


# --- Morphology layer (from the Quranic Arabic Corpus) ---


class Root(Vertex):
    "A root shared by a family of lemmas, for example رحم"

    __label__ = "Root"

    id: str  # the root letters
    root: str
    letters: int


class Lemma(Vertex):
    "Dictionary form of a word as spelled in the corpus, for example رَحِيم"

    __label__ = "Lemma"

    id: str  # the lemma itself
    lemma: str
    root: str | None = None
    pos: str  # N, V or P


class Token(Vertex):
    "One word occurrence in the Uthmani text with its morphology"

    __label__ = "Token"

    id: str  # "surah:aya:position"
    surah_number: int
    aya_number: int
    position: int
    text: str  # Uthmani form
    text_simple: str = ""  # the matching token(s) of the simple-clean text
    tag: str  # N, V or P of the stem
    root: str | None = None
    lemma: str | None = None
    features: str = ""  # stem features, for example "ROOT:رحم|LEM:رَحِيم|MS|GEN|ADJ"
    segments: list[dict] = Field(default_factory=list)  # every segment: form, tag, features
    glosses: dict[str, str] = Field(default_factory=dict)  # language -> meaning in this aya


class HasToken(Edge):
    "Links Aya to its Tokens in reading order"

    __label__ = "HAS_TOKEN"

    position: int


class HasLemma(Edge):
    "Links Token to its Lemma"

    __label__ = "HAS_LEMMA"


class HasRoot(Edge):
    "Links Lemma to its Root"

    __label__ = "HAS_ROOT"


class IsForm(Edge):
    "Links Token to the simple-text Word it is written as"

    __label__ = "IS_FORM"


# --- Topics, themes and related verses (from QUL) ---


class Topic(Vertex):
    "A concept or subject in the Quran, with thematic and ontology hierarchies"

    __label__ = "Topic"

    id: str  # QUL topic id as a string
    name: str
    arabic_name: str = ""
    description: str = ""  # HTML; <topic data-id> links are rewritten by the API
    wiki_link: str = ""
    thematic: bool = False
    ontology: bool = False
    aya_count: int = 0


class Theme(Vertex):
    "A theme covering a range of ayas in one surah"

    __label__ = "Theme"

    id: str  # "theme:<n>"
    theme: str
    surah_number: int
    aya_from: int
    aya_to: int
    keywords: str = ""


class Phrase(Vertex):
    "A phrase that recurs across ayas (mutashabihat)"

    __label__ = "Phrase"

    id: str  # "phrase:<n>"
    text: str  # Uthmani words of the source occurrence
    source_aya: str
    source_from: int
    source_to: int
    aya_count: int = 0


class HasTopic(Edge):
    "Links Aya to a Topic it is about"

    __label__ = "HAS_TOPIC"


class ChildOf(Edge):
    "Links a Topic to its parent in one of the hierarchies"

    __label__ = "CHILD_OF"

    kind: str  # parent, thematic or ontology


class RelatedTopic(Edge):
    "Links related Topics"

    __label__ = "RELATED_TOPIC"


class HasTheme(Edge):
    "Links Aya to a Theme covering it"

    __label__ = "HAS_THEME"


class SimilarTo(Edge):
    "Links an Aya to a similar Aya"

    __label__ = "SIMILAR_TO"

    score: int = 0
    coverage: int = 0
    matched_words: int = 0
    match_words: list = Field(default_factory=list)  # [[from, to], ...] word positions


class HasPhrase(Edge):
    "Links Aya to a Phrase it contains, with the word positions"

    __label__ = "HAS_PHRASE"

    ranges: list = Field(default_factory=list)  # [[from, to], ...]
