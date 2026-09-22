"""Quranic Arabic Corpus morphology: parsing and alignment with the simple text.

The corpus annotates every word of the Uthmani text as one or more segments
(prefix, stem, suffix), each with a tag (N, V, P) and features such as
``ROOT:رحم`` and ``LEM:رَحِيم``. This module parses that file and aligns each
annotated word with the token(s) of our diacritic-free "simple-clean" text,
whose spelling (imlaei) differs from the Uthmani script in predictable ways.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from .textnorm import normalize_for_search

# Standalone pause, sajda and similar marks that appear as tokens in Tanzil's simple text.
_PAUSE_MARK = re.compile(r"^[ۖ-ۭـ]+$")


def is_pause_mark(token: str) -> bool:
    """True for a token that is only a Quranic pause or sajda sign, not a word."""
    return bool(_PAUSE_MARK.match(token))


@dataclass
class Segment:
    form: str
    tag: str
    features: str

    @property
    def feature_list(self) -> list[str]:
        return self.features.split("|") if self.features else []

    @property
    def is_affix(self) -> bool:
        return "PREF" in self.feature_list or "SUFF" in self.feature_list

    def feature(self, key: str) -> str | None:
        """Value of a ``KEY:value`` feature, or None."""
        prefix = key + ":"
        for f in self.feature_list:
            if f.startswith(prefix):
                return f[len(prefix) :]
        return None

    def as_dict(self) -> dict:
        return {"form": self.form, "tag": self.tag, "features": self.features}


@dataclass
class MorphWord:
    surah: int
    aya: int
    position: int
    segments: list[Segment] = field(default_factory=list)

    @property
    def location(self) -> str:
        return f"{self.surah}:{self.aya}:{self.position}"

    @property
    def aya_key(self) -> str:
        return f"{self.surah}:{self.aya}"

    @property
    def text(self) -> str:
        return "".join(s.form for s in self.segments)

    @property
    def stem(self) -> Segment:
        """The segment carrying the word's own meaning (first non-affix segment)."""
        for s in self.segments:
            if not s.is_affix:
                return s
        return self.segments[0]

    @property
    def root(self) -> str | None:
        return self.stem.feature("ROOT")

    @property
    def lemma(self) -> str | None:
        return self.stem.feature("LEM")

    @property
    def tag(self) -> str:
        return self.stem.tag


_LOCATION = re.compile(r"^\(?(\d+):(\d+):(\d+):(\d+)\)?$")


def parse_morphology(path: Path) -> list[MorphWord]:
    """Parse a corpus morphology file into words ordered by location.

    Accepts both the original layout, ``(1:1:1:1)`` locations with a header,
    and the plain ``1:1:1:1`` layout of the Arabic-script mirror.
    """
    words: dict[tuple[int, int, int], MorphWord] = {}
    with open(path, encoding="utf-8") as fp:
        for line in fp:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 4:
                continue
            m = _LOCATION.match(parts[0].strip())
            if not m:
                continue
            surah, aya, position, _segment = (int(x) for x in m.groups())
            word = words.setdefault((surah, aya, position), MorphWord(surah, aya, position))
            word.segments.append(Segment(parts[1], parts[2], parts[3]))
    return [words[k] for k in sorted(words)]


# --- Alignment ---

_SKELETON_DROP = re.compile(r"[اء]")


def skeleton(text: str) -> str:
    """Consonantal skeleton used to compare Uthmani and imlaei spellings.

    Uthmani spelling omits or adds alefs (الكتب / الكتاب), writes ى for ي and
    ءا for آ; dropping alef and hamza after normalization makes both spellings
    of a word compare equal in nearly every case.
    """
    return _SKELETON_DROP.sub("", normalize_for_search(text).replace("ة", "ه"))


# A merge (one word on one side, two on the other) must look like a real match.
_MERGE_MIN_SIMILARITY = 0.75
_MERGE_PENALTY = 0.1


def _similarity(a: str, b: str) -> float:
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def align_words(morph_texts: list[str], simple_tokens: list[str]) -> list[list[int]]:
    """Map each morphology word to the index(es) of its simple-text token(s).

    Usually one index per word. Two indexes when the simple text splits a word
    the Uthmani text writes as one (يا أيها for يَٰٓأَيُّهَا). An empty list when a
    word has no counterpart. ``simple_tokens`` must not contain pause marks.
    """
    m = [skeleton(t) for t in morph_texts]
    s = [skeleton(t) for t in simple_tokens]
    n, k = len(m), len(s)
    if n == k and m == s:
        return [[i] for i in range(n)]

    inf = float("inf")
    cost = [[inf] * (k + 1) for _ in range(n + 1)]
    back: list[list[tuple[int, int, int] | None]] = [[None] * (k + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0
    for i in range(n + 1):
        for j in range(k + 1):
            c = cost[i][j]
            if c == inf:
                continue
            if i < n and j < k:
                v = c + (1 - _similarity(m[i], s[j]))
                if v < cost[i + 1][j + 1]:
                    cost[i + 1][j + 1], back[i + 1][j + 1] = v, (i, j, 1)
            if i < n and j + 1 < k:  # one Uthmani word, two simple tokens
                sim = _similarity(m[i], s[j] + s[j + 1])
                v = c + (1 - sim) + _MERGE_PENALTY
                if sim >= _MERGE_MIN_SIMILARITY and v < cost[i + 1][j + 2]:
                    cost[i + 1][j + 2], back[i + 1][j + 2] = v, (i, j, 2)
            if i + 1 < n and j < k:  # two Uthmani words, one simple token
                sim = _similarity(m[i] + m[i + 1], s[j])
                v = c + (1 - sim) + _MERGE_PENALTY
                if sim >= _MERGE_MIN_SIMILARITY and v < cost[i + 2][j + 1]:
                    cost[i + 2][j + 1], back[i + 2][j + 1] = v, (i, j, 3)
            if i < n:  # word without a counterpart
                v = c + 1.0
                if v < cost[i + 1][j]:
                    cost[i + 1][j], back[i + 1][j] = v, (i, j, 4)
            if j < k:  # token without a counterpart
                v = c + 1.0
                if v < cost[i][j + 1]:
                    cost[i][j + 1], back[i][j + 1] = v, (i, j, 5)

    result: list[list[int]] = [[] for _ in range(n)]
    i, j = n, k
    while (i, j) != (0, 0):
        step = back[i][j]
        assert step is not None
        pi, pj, kind = step
        if kind == 1:
            result[pi] = [pj]
        elif kind == 2:
            result[pi] = [pj, pj + 1]
        elif kind == 3:
            result[pi] = [pj]
            result[pi + 1] = [pj]
        i, j = pi, pj
    return result
