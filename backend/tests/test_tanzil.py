"""Tests for the Tanzil refresh helpers."""

from quranref.tanzil import (
    TextDiff,
    all_source_ids,
    apply_diff,
    diff_texts,
    graph_texts,
    parse_tanzil,
    prune_orphan_texts,
    source_name,
    split_bismillah,
)

SAMPLE = """1|1|In the name of Allah
1|2|Praise be to Allah
2|1|In the name of Allah Alif Lam Meem

# ---
#  Quran Translation
#  Name: Test
#  ID: en.test
#  Last Update: April 24, 2011
# ---
"""


def test_parse_tanzil_reads_ayas_and_footer():
    parsed = parse_tanzil(SAMPLE)
    assert parsed.ayas == {
        "1:1": "In the name of Allah",
        "1:2": "Praise be to Allah",
        "2:1": "In the name of Allah Alif Lam Meem",
    }
    assert parsed.meta["Last Update"] == "April 24, 2011"
    assert parsed.meta["ID"] == "en.test"


def test_parse_skips_empty_ayas():
    parsed = parse_tanzil("80|38|text\n80|39|\n80|40|more\n")
    assert list(parsed.ayas) == ["80:38", "80:40"]


def test_parse_keeps_next_line_characters_inside_a_line():
    parsed = parse_tanzil("2|140|knows better\u0085 that they all\n2|141|next\n")
    assert parsed.ayas["2:140"] == "knows better\u0085 that they all"
    assert parsed.ayas["2:141"] == "next"


def test_split_bismillah_moves_the_prefix_to_aya_zero():
    texts = split_bismillah(parse_tanzil(SAMPLE).ayas)
    assert texts["2:0"] == "In the name of Allah"
    assert texts["2:1"] == "Alif Lam Meem"
    assert texts["1:1"] == "In the name of Allah"
    # a first aya that is only the bismillah (as in some translations) is left alone
    assert split_bismillah({"1:1": "B", "9:1": "B"}) == {"1:1": "B", "9:1": "B"}


def test_cosmetic_changes_are_reported_separately():
    shadda_then_damma = "\u064a\u0651\u064f"
    damma_then_shadda = "\u064a\u064f\u0651"
    diff = diff_texts(
        {"1:1": damma_then_shadda, "1:2": "x"}, {"1:1": shadda_then_damma, "1:2": "y"}
    )
    assert [c[0] for c in diff.changed] == ["1:1", "1:2"]
    assert diff.cosmetic() == ["1:1"]


def test_diff_texts():
    diff = diff_texts({"1:1": "a", "1:2": "b", "1:3": "c"}, {"1:1": "a", "1:2": "B", "1:4": "d"})
    assert diff.changed == [("1:2", "b", "B")]
    assert diff.added == ["1:4"]
    assert diff.removed == ["1:3"]
    assert len(diff) == 3
    assert len(TextDiff()) == 0


def test_source_ids_and_names():
    assert source_name("en.sahih") == ("english", "sahih-international")
    assert source_name("quran:uthmani-min") == ("arabic", "uthmani-minimal")
    assert len(all_source_ids()) == 121
    assert all_source_ids()[0] == "quran:simple"


def test_apply_diff_replaces_texts_in_the_graph(test_graph, test_db):
    g = test_graph
    before = graph_texts(g, "english", "maududi")
    assert before["1:2"] == "All praise is due to Allah Lord of the worlds"
    fresh = dict(before)
    fresh["1:2"] = "All praise is due to Allah, Lord of all the worlds"
    fresh["2:0"] = "In the name of Allah"
    diff = diff_texts(before, fresh)
    assert [c[0] for c in diff.changed] == ["1:2"] and diff.added == ["2:0"]

    apply_diff(g, "english", "maududi", fresh, diff)
    after = graph_texts(g, "english", "maududi")
    assert after["1:2"] == fresh["1:2"] and after["2:0"] == "In the name of Allah"
    assert len(after) == len(before) + 1
    assert prune_orphan_texts(test_db) == 1  # the old 1:2 text is no longer referenced

    # put the fixture back for the other tests
    restore = diff_texts(after, before)
    apply_diff(g, "english", "maududi", before, restore)
    assert graph_texts(g, "english", "maududi") == before
    prune_orphan_texts(test_db)
