from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class AyaResultSchema(BaseModel):
    """
    aya_key is a string in the format of "{surah_number}:{aya_number}"

    texts is a dictionary of dictionaries {language: {text_type: text, ...}, ...}
    where the outer dictionary is keyed by language and the inner dictionary is keyed by text type

    example: {"english": {"maududi": "In the name of Allah, the Entirely Merciful, the Especially Merciful."}}
    """

    aya_key: str
    texts: dict[str, dict[str, str]]


# --- Bookmark schemas ---


def _validate_aya_key(v: str) -> str:
    import re

    if not re.match(r"^\d+:\d+$", v):
        raise ValueError("aya_key must be in format 'surah:aya' (e.g. '1:1')")
    return v


class BookmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bookmark_type: str
    aya_key: str
    note: str
    created_at: datetime
    updated_at: datetime


class BookmarksListResponse(BaseModel):
    reading: BookmarkResponse | None
    notes: list[BookmarkResponse]


class ReadingBookmarkRequest(BaseModel):
    aya_key: str

    @field_validator("aya_key")
    @classmethod
    def check_aya_key(cls, v: str) -> str:
        return _validate_aya_key(v)


class NoteBookmarkRequest(BaseModel):
    aya_key: str
    note: str

    @field_validator("aya_key")
    @classmethod
    def check_aya_key(cls, v: str) -> str:
        return _validate_aya_key(v)


class NoteBookmarkUpdateRequest(BaseModel):
    note: str


# --- Word morphology schemas ---


class TokenSchema(BaseModel):
    """One word of an aya with its morphology."""

    position: int
    text: str
    text_simple: str = ""
    tag: str
    root: str | None = None
    lemma: str | None = None
    features: str = ""
    segments: list[dict] = []
    glosses: dict[str, str] = {}


class LemmaOccurrenceSchema(BaseModel):
    aya_key: str
    position: int
    text: str
    text_simple: str = ""
    glosses: dict[str, str] = {}
    aya_text: str = ""


class LemmaMeaningSchema(BaseModel):
    gloss: str
    count: int


class LemmaSchema(BaseModel):
    lemma: str
    pos: str
    root: str | None = None
    count: int
    meanings: dict[str, list[LemmaMeaningSchema]]
    occurrences: list[LemmaOccurrenceSchema]


class RootLemmaSchema(BaseModel):
    lemma: str
    pos: str
    count: int


class RootSchema(BaseModel):
    root: str
    letters: int
    count: int
    lemmas: list[RootLemmaSchema]


class WordMorphologySchema(BaseModel):
    lemma: str | None = None
    root: str | None = None
    pos: str | None = None
    count: int


# --- Topics, themes, related verses ---


class TopicSummarySchema(BaseModel):
    id: str
    name: str
    arabic_name: str = ""
    aya_count: int = 0
    thematic: bool = False
    ontology: bool = False
    parent_id: str | None = None
    thematic_parent_id: str | None = None
    ontology_parent_id: str | None = None


class TopicSchema(BaseModel):
    id: str
    name: str
    arabic_name: str = ""
    description: str = ""
    wiki_link: str = ""
    thematic: bool = False
    ontology: bool = False
    aya_count: int = 0
    parents: list[TopicSummarySchema] = []
    children: list[TopicSummarySchema] = []
    related: list[TopicSummarySchema] = []


class ThemeSchema(BaseModel):
    id: str
    theme: str
    surah_number: int
    aya_from: int
    aya_to: int
    keywords: str = ""


class AyaTopicsSchema(BaseModel):
    topics: list[TopicSummarySchema] = []
    themes: list[ThemeSchema] = []


class AyaPageSchema(BaseModel):
    total: int
    offset: int
    ayas: list[AyaResultSchema]


class SimilarAyaSchema(BaseModel):
    aya_key: str
    score: int = 0
    coverage: int = 0
    matched_words: int = 0
    match_words: list = []
    texts: dict[str, dict[str, str]] = {}


class PhraseSchema(BaseModel):
    id: str
    text: str
    source_aya: str
    aya_count: int = 0
    ranges: list = []  # positions in the aya being asked about, when applicable
    aya_keys: list[str] = []


class RelatedSchema(BaseModel):
    similar: list[SimilarAyaSchema] = []
    phrases: list[PhraseSchema] = []


# --- Mushaf structure ---


class AyaStructureSchema(BaseModel):
    aya_key: str
    juz: int | None = None
    hizb: int | None = None
    rub: int | None = None
    manzil: int | None = None
    ruku: int | None = None
    surah_ruku: int | None = None
    sajda: str | None = None


class SurahMarkerSchema(BaseModel):
    aya_number: int
    juz_start: int | None = None
    hizb_start: int | None = None
    rub_start: int | None = None
    manzil_start: int | None = None
    ruku_start: int | None = None
    sajda: str | None = None


class SurahInfoSchema(BaseModel):
    surah_number: int
    language: str
    available: list[str]
    text: str
    short_text: str = ""
