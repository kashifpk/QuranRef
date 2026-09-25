"""Helpers for fetching aya texts in the language specs the API uses."""

from age_orm import Graph

from .schemas import AyaResultSchema


def aya_sort_key(aya_key: str) -> tuple[int, int]:
    surah, aya = aya_key.split(":", 1)
    return int(surah), int(aya)


def _build_language_filter(languages_spec: str, edge_alias: str = "e") -> tuple[str, dict]:
    """Build a Cypher WHERE clause for language/text_type filtering.

    Returns (clause_string, params_dict).
    """
    parts = []
    params = {}
    for idx, lang in enumerate(languages_spec.split("_")):
        language, text_type = lang.split(":")
        lang_param = f"lang_{idx}"
        tt_param = f"tt_{idx}"
        parts.append(
            f"({edge_alias}.language = ${lang_param} AND {edge_alias}.text_type = ${tt_param})"
        )
        params[lang_param] = language
        params[tt_param] = text_type

    return " OR ".join(parts), params


def _process_aya_results(results: list[dict]) -> list[AyaResultSchema]:
    """Process raw Cypher results into AyaResultSchema list.

    Each result row has: aya_id, language, text_type, text
    """
    ayas_dict: dict[str, AyaResultSchema] = {}

    for r in results:
        aya_key = r["aya_id"]
        if aya_key not in ayas_dict:
            ayas_dict[aya_key] = AyaResultSchema(aya_key=aya_key, texts={})

        lang = r["language"]
        text_type = r["text_type"]
        text = r["text"]

        if lang not in ayas_dict[aya_key].texts:
            ayas_dict[aya_key].texts[lang] = {}

        ayas_dict[aya_key].texts[lang][text_type] = text

    return list(ayas_dict.values())


def ayas_with_texts(g: Graph, aya_keys: list[str], languages_spec: str) -> list[AyaResultSchema]:
    """Texts for the given ayas in the given languages, in the order of aya_keys."""
    if not aya_keys:
        return []
    lang_filter, lang_params = _build_language_filter(languages_spec)
    rows = g.cypher(
        "MATCH (a:Aya)-[e:AYA_TEXT]->(t:Text) "
        f"WHERE a.id IN $keys AND ({lang_filter}) "
        "RETURN a.id, e.language, e.text_type, t.text",
        columns=["aya_id", "language", "text_type", "text"],
        keys=aya_keys,
        **lang_params,
    )
    order = {k: i for i, k in enumerate(aya_keys)}
    results = _process_aya_results(rows)
    results.sort(key=lambda a: order.get(a.aya_key, len(order)))
    return results
