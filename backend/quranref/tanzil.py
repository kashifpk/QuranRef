"""Refresh the Arabic texts and translations from tanzil.net.

Tanzil publishes each text as ``surah|aya|text`` lines followed by a comment footer that
names the text and its last update. The bundled copies under backend/data are what
``db import-text`` loads; this module downloads the current files, compares them with the
bundled copies and with the graph, and applies the changed ayas in place.
"""

import bz2
import re
import unicodedata
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from age_orm import Graph

from . import PROJECT_ROOT
from .data.tanzil import QURAN_TEXTS, TRANSLATIONS
from .models import Aya, AyaText

TRANSLATION_URL = "https://tanzil.net/trans/?transID={tid}&type=txt-2"
# The options match the bundled files: pause marks, sajdah signs, superscript alefs with
# tatweel, no rub-el-hizb signs. Text with verse numbers (txt-2).
QURAN_URL = (
    "https://tanzil.net/pub/download/index.php?quranType={qtype}&outType=txt-2"
    "&marks=true&sajdah=true&alef=true&tatweel=true&agree=true"
)
USER_AGENT = "QuranRef/2.0 (+https://quranref.info)"
DATA_DIR = PROJECT_ROOT / "data"

_META_RE = re.compile(r"^#\s+([A-Za-z ]+?):\s*(.+?)\s*$")


@dataclass
class TanzilText:
    ayas: dict[str, str] = field(default_factory=dict)  # "surah:aya" -> text
    meta: dict[str, str] = field(default_factory=dict)  # footer fields (Name, Last Update, ...)


@dataclass
class TextDiff:
    changed: list[tuple[str, str, str]] = field(default_factory=list)  # key, old, new
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.changed) + len(self.added) + len(self.removed)

    def cosmetic(self) -> list[str]:
        """Keys whose old and new text are the same after Unicode normalization.

        Tanzil writes combining marks in its own order; some texts in the graph were stored
        in canonical (NFC) order, which renders identically.
        """
        return [key for key, old, new in self.changed if same_text(old, new)]


def same_text(a: str, b: str) -> bool:
    return unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b)


def parse_tanzil(content: str) -> TanzilText:
    """Parse a Tanzil text-with-verse-numbers file."""
    result = TanzilText()
    # Split on newlines only: str.splitlines() would also break on U+0085 (NEL), which
    # occurs inside some translation lines.
    for line in content.split("\n"):
        line = line.rstrip("\r")
        if line.startswith("#"):
            m = _META_RE.match(line)
            if m:
                result.meta[m.group(1)] = m.group(2)
            continue
        if "|" not in line:
            continue
        surah, aya, text = line.split("|", 2)
        text = text.strip()
        if text:  # a few translations leave an aya empty; import-text skips those too
            result.ayas[f"{int(surah)}:{int(aya)}"] = text
    return result


def split_bismillah(ayas: dict[str, str]) -> dict[str, str]:
    """Move a leading bismillah on the first aya of a surah into aya 0, as import-text does."""
    bismillah = ayas.get("1:1", "")
    if not bismillah:
        return dict(ayas)
    result = {}
    for key, text in ayas.items():
        surah, aya = key.split(":")
        if aya == "1" and surah != "1" and text.startswith(bismillah):
            rest = text[len(bismillah) :].strip()
            if rest:
                result[f"{surah}:0"] = bismillah
                text = rest
        result[key] = text
    return result


def source_name(source_id: str) -> tuple[str, str]:
    """(language, text_type) for a translation id or a ``quran:<type>`` id."""
    if source_id.startswith("quran:"):
        qtype = source_id[len("quran:") :]
        if qtype not in QURAN_TEXTS:
            raise KeyError(source_id)
        return "arabic", QURAN_TEXTS[qtype]
    if source_id not in TRANSLATIONS:
        raise KeyError(source_id)
    return TRANSLATIONS[source_id]


def all_source_ids() -> list[str]:
    return [f"quran:{q}" for q in QURAN_TEXTS] + sorted(TRANSLATIONS)


def bundled_path(source_id: str) -> Path:
    if source_id.startswith("quran:"):
        return DATA_DIR / f"quran-{source_id[len('quran:') :]}.txt.bz2"
    return DATA_DIR / "translations" / f"{source_id}.txt.bz2"


def read_bundled(source_id: str) -> str | None:
    path = bundled_path(source_id)
    if not path.exists():
        return None
    with bz2.open(path, "rt", encoding="utf-8") as fp:
        return fp.read()


def write_bundled(source_id: str, content: str) -> Path:
    path = bundled_path(source_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with bz2.open(path, "wt", encoding="utf-8") as fp:
        fp.write(content)
    return path


def download_url(source_id: str) -> str:
    if source_id.startswith("quran:"):
        return QURAN_URL.format(qtype=source_id[len("quran:") :])
    return TRANSLATION_URL.format(tid=source_id)


def download(source_id: str, timeout: int = 120) -> str:
    request = urllib.request.Request(download_url(source_id), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as resp:  # nosec B310
        content = resp.read().decode("utf-8")
    if "|" not in content:
        raise ValueError(f"{source_id}: the download does not look like a Tanzil text file")
    return content


def graph_texts(g: Graph, language: str, text_type: str) -> dict[str, str]:
    rows = g.cypher(
        "MATCH (a:Aya)-[e:AYA_TEXT]->(t:Text) "
        "WHERE e.language = $language AND e.text_type = $text_type RETURN a.id, t.text",
        columns=["aya_key", "text"],
        language=language,
        text_type=text_type,
    )
    return {r["aya_key"]: r["text"] for r in rows}


def diff_texts(current: dict[str, str], fresh: dict[str, str]) -> TextDiff:
    diff = TextDiff()
    for key, text in fresh.items():
        if key not in current:
            diff.added.append(key)
        elif current[key] != text:
            diff.changed.append((key, current[key], text))
    diff.removed = [key for key in current if key not in fresh]
    return diff


def apply_diff(g: Graph, language: str, text_type: str, fresh: dict[str, str], diff: TextDiff):
    """Replace the AYA_TEXT edges of the changed, added and removed ayas."""
    for key in [c[0] for c in diff.changed] + diff.removed:
        g.cypher(
            "MATCH (a:Aya {id: $key})-[e:AYA_TEXT {language: $language, text_type: $text_type}]"
            "->(:Text) DELETE e",
            key=key,
            language=language,
            text_type=text_type,
        )
    for key in [c[0] for c in diff.changed] + diff.added:
        surah, aya = key.split(":")
        aya_doc = Aya.get_or_new(g, int(surah), int(aya))
        AyaText.new(g, aya_doc, fresh[key], language, text_type)


def prune_orphan_texts(g: Graph) -> int:
    """Delete Text vertices no aya points at any more (left behind by replaced texts)."""
    rows = g.cypher(
        "MATCH (t:Text) WHERE NOT EXISTS((:Aya)-[:AYA_TEXT]->(t)) DELETE t RETURN count(*)",
        columns=["deleted"],
    )
    return int(rows[0]["deleted"]) if rows else 0
