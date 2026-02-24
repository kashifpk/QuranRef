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
