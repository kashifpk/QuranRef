"""Unit tests for the morphology parser and alignment (no database needed)."""

from pathlib import Path

from quranref.morphology import (
    MorphWord,
    Segment,
    align_words,
    is_pause_mark,
    parse_morphology,
    skeleton,
)

SAMPLE = """\
1:1:1:1\tبِ\tP\tP|PREF|LEM:ب
1:1:1:2\tسْمِ\tN\tROOT:سمو|LEM:اسْم|M|GEN
1:1:2:1\tٱللَّهِ\tN\tPN|ROOT:أله|LEM:اللَّه|GEN
(1:1:3:1)\tٱل\tP\tDET|PREF|LEM:ال
(1:1:3:2)\tرَّحْمَٰنِ\tN\tROOT:رحم|LEM:رَحْمٰن|MS|GEN|ADJ
2:255:5:1\tهُوَ\tN\tPRON|3MS
"""


def test_parse_groups_segments_into_words(tmp_path: Path):
    path = tmp_path / "morph.txt"
    path.write_text("LOCATION\tFORM\tTAG\tFEATURES\n" + SAMPLE, encoding="utf-8")
    words = parse_morphology(path)
    assert [w.location for w in words] == ["1:1:1", "1:1:2", "1:1:3", "2:255:5"]
    bism = words[0]
    assert bism.text == "بِسْمِ"
    assert bism.stem.form == "سْمِ"
    assert bism.root == "سمو"
    assert bism.lemma == "اسْم"
    assert bism.tag == "N"
    assert len(bism.segments) == 2
    assert words[2].root == "رحم" and words[2].lemma == "رَحْمٰن"
    pronoun = words[3]
    assert pronoun.root is None and pronoun.lemma is None and pronoun.tag == "N"


def test_segment_helpers():
    seg = Segment("ٱل", "P", "DET|PREF|LEM:ال")
    assert seg.is_affix
    assert seg.feature("LEM") == "ال"
    assert seg.feature("ROOT") is None
    assert seg.as_dict() == {"form": "ٱل", "tag": "P", "features": "DET|PREF|LEM:ال"}


def test_stem_falls_back_to_first_segment():
    word = MorphWord(1, 1, 1, [Segment("وَ", "P", "CONJ|PREF|LEM:و")])
    assert word.stem.form == "وَ"


def test_pause_marks():
    assert is_pause_mark("ۚ")
    assert is_pause_mark("۩")
    assert not is_pause_mark("الله")
    assert not is_pause_mark("ص")


def test_skeleton_equates_uthmani_and_imlaei_spellings():
    assert skeleton("ٱلْكِتَٰبُ") == skeleton("الكتاب")
    assert skeleton("فِى") == skeleton("في")
    assert skeleton("ٱلسَّمَٰوَٰتِ") == skeleton("السماوات")
    assert skeleton("ءَامَنُوا۟") == skeleton("آمنوا")


def test_align_identical_lengths():
    morph = ["بِسْمِ", "ٱللَّهِ", "ٱلرَّحْمَٰنِ", "ٱلرَّحِيمِ"]
    simple = ["بسم", "الله", "الرحمن", "الرحيم"]
    assert align_words(morph, simple) == [[0], [1], [2], [3]]


def test_align_merges_split_vocative():
    # Uthmani writes يَٰٓأَيُّهَا as one word; the simple text has يا أيها
    morph = ["يَٰٓأَيُّهَا", "ٱلَّذِينَ", "ءَامَنُوا۟"]
    simple = ["يا", "أيها", "الذين", "آمنوا"]
    assert align_words(morph, simple) == [[0, 1], [2], [3]]


def test_align_tolerates_spelling_differences():
    morph = ["وَأَقِيمُوا۟", "ٱلصَّلَوٰةَ", "وَءَاتُوا۟", "ٱلزَّكَوٰةَ"]
    simple = ["وأقيموا", "الصلاة", "وآتوا", "الزكاة"]
    assert align_words(morph, simple) == [[0], [1], [2], [3]]


def test_align_leaves_unmatched_word_empty():
    assert align_words(["ٱللَّهِ", "ٱلرَّحْمَٰنِ"], ["الله"]) == [[0], []]
    assert align_words([], []) == []
