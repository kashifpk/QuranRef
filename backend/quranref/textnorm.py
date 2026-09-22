"""Text normalization for search.

Both stored texts and search terms go through ``normalize_for_search`` so that a
query without diacritics matches diacritized text, Arabic letter variants match
each other, and Latin-script searches are case and accent insensitive.
"""

import re
import unicodedata

# Tashkeel, Quranic annotation signs, pause marks, tatweel and the small alef.
_ARABIC_MARKS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")

# Letter variants that readers do not distinguish when searching. Arabic and Urdu
# both use this script; Urdu spells some letters with its own code points.
_LETTER_MAP = str.maketrans(
    {
        "ٱ": "ا",
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٲ": "ا",
        "ٳ": "ا",
        "ى": "ي",
        "ی": "ي",
        "ې": "ي",
        "ے": "ي",
        "ك": "ک",
        "ہ": "ه",
        "ۂ": "ه",
        "ھ": "ه",
        "ۃ": "ة",
        "ؤ": "و",
        "ئ": "ي",
    }
)

_WHITESPACE = re.compile(r"\s+")


def normalize_for_search(text: str) -> str:
    """Return a normalized form of ``text`` suitable for substring search."""
    if not text:
        return ""
    # NFKD splits accented Latin letters and Arabic ligatures into base + marks.
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    stripped = _ARABIC_MARKS.sub("", stripped)
    stripped = stripped.translate(_LETTER_MAP)
    return _WHITESPACE.sub(" ", stripped).strip().casefold()
