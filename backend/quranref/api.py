import json
import logging

from age_orm import Graph
from fastapi import APIRouter, Depends, HTTPException, status

from .db import graph, raw_connection
from .models import Surah, Word
from .schemas import AyaResultSchema

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/letters")
async def get_letters() -> list[str]:
    """
    Get all letters
    """
    letters_list: list[str] = [
        "آ",
        "أ",
        "إ",
        "ا",
        "ب",
        "ت",
        "ث",
        "ج",
        "ح",
        "خ",
        "د",
        "ذ",
        "ر",
        "ز",
        "س",
        "ش",
        "ص",
        "ض",
        "ط",
        "ظ",
        "ع",
        "غ",
        "ف",
        "ق",
        "ك",
        "ل",
        "م",
        "ن",
        "و",
        "ه",
        "ي",
    ]
    return letters_list


@router.get("/surahs")
async def get_surahs(g: Graph = Depends(graph)) -> list[Surah]:
    """
    Get all Surahs
    """
    surahs: list[Surah] = g.query(Surah).sort("n.surah_number").all()
    return surahs


@router.get("/text-types")
async def get_text_types() -> dict[str, list[str]]:
    """
    Get all text types
    """
    with raw_connection() as conn:
        result = conn.execute(
            "SELECT value FROM meta_info WHERE key = %s", ("text-types",)
        ).fetchone()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Text types not found"
        )

    value = result[0]
    if isinstance(value, str):
        value = json.loads(value)
    return value


@router.get("/words-by-letter/{arabic_letter}")
async def get_words_by_letter(
    arabic_letter: str, g: Graph = Depends(graph)
) -> list[tuple[str, int]]:
    """
    Get all words starting with the given Arabic letter
    """
    results = g.cypher(
        "MATCH (w:Word) WHERE left(w.word, 1) = $letter "
        'RETURN w.word, w["count"]',
        columns=["word", "count"],
        letter=arabic_letter,
    )

    results.sort(key=lambda r: r["word"])
    return [(r["word"], r["count"]) for r in results]


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


@router.get("/ayas-by-word/{word}/{languages}")
async def get_ayas_by_word(
    word: str, languages: str, g: Graph = Depends(graph)
) -> list[AyaResultSchema]:
    """
    Get all ayas containing the given word and return text in the given languages.
    """
    word_doc = g.query(Word).filter_by(word=word).first()
    if word_doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")

    lang_filter, lang_params = _build_language_filter(languages)

    results = g.cypher(
        "MATCH (a:Aya)-[:HAS_WORD]->(w:Word), (a)-[e:AYA_TEXT]->(t:Text) "
        f"WHERE id(w) = $word_gid AND ({lang_filter}) "
        "RETURN a.id, e.language, e.text_type, t.text",
        columns=["aya_id", "language", "text_type", "text"],
        word_gid=word_doc.graph_id,
        **lang_params,
    )

    results.sort(key=lambda r: r["aya_id"])
    return _process_aya_results(results)


@router.get("/words-by-count/{count}")
async def get_words_by_count(count: int, g: Graph = Depends(graph)) -> list[tuple[str, int]]:
    """
    Get all words with the given count
    """
    results = g.cypher(
        'MATCH (w:Word) WHERE w["count"] = $cnt RETURN w.word, w["count"]',
        columns=["word", "count"],
        cnt=count,
    )
    results.sort(key=lambda r: r["word"])
    return [(r["word"], r["count"]) for r in results]


@router.get("/available-word-counts")
async def get_available_word_counts(g: Graph = Depends(graph)) -> list[dict]:
    """
    Get all available word counts with the number of words for each count.
    Returns a list of {count, word_count} objects sorted by count descending.
    """
    results = g.cypher(
        'MATCH (w:Word) RETURN w["count"], count(w)',
        columns=["count", "word_count"],
    )
    results.sort(key=lambda r: r["count"], reverse=True)
    return [{"count": r["count"], "word_count": r["word_count"]} for r in results]


@router.get("/top-most-frequent-words/{limit}")
async def get_top_most_frequent_words(
    limit: int, g: Graph = Depends(graph)
) -> list[tuple[str, int]]:
    """
    Get top most frequent words
    """
    results = g.cypher(
        'MATCH (w:Word) RETURN w.word, w["count"]',
        columns=["word", "count"],
    )
    results.sort(key=lambda r: (-r["count"], r["word"]))
    return [(r["word"], r["count"]) for r in results[:limit]]


@router.get("/text/{ayas_spec}/{languages_spec}")
async def get_text(
    ayas_spec: str, languages_spec: str, g: Graph = Depends(graph)
) -> list[AyaResultSchema]:
    """
    Get text for the given ayas and languages.
    """

    surah_number = None
    aya_num_or_range = None

    if "-" not in ayas_spec and ":" not in ayas_spec:
        surah_number = ayas_spec
    else:
        surah_number, aya_num_or_range = ayas_spec.split(":", 1)

    if surah_number is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid surah number"
        )

    lang_filter, lang_params = _build_language_filter(languages_spec)

    # Build Cypher query
    cypher = (
        "MATCH (s:Surah)-[:HAS_AYA]->(a:Aya)-[e:AYA_TEXT]->(t:Text) "
        f"WHERE s.id = $surah_num AND ({lang_filter})"
    )
    params = {"surah_num": surah_number, **lang_params}

    # Add aya filter
    if aya_num_or_range is not None:
        if "-" in aya_num_or_range:
            start_aya, end_aya = aya_num_or_range.split("-", 1)
            cypher += " AND a.aya_number >= $start_aya AND a.aya_number <= $end_aya"
            params["start_aya"] = int(start_aya)
            params["end_aya"] = int(end_aya)
        else:
            cypher += " AND a.aya_number = $aya_num"
            params["aya_num"] = int(aya_num_or_range)

    cypher += " RETURN a.id, e.language, e.text_type, t.text"

    results = g.cypher(
        cypher,
        columns=["aya_id", "language", "text_type", "text"],
        **params,
    )

    # Sort by aya number (extracted from id like "1:3")
    results.sort(key=lambda r: int(r["aya_id"].split(":")[1]))

    return _process_aya_results(results)


@router.get("/search/{search_term}/{search_language_spec}/{translation_languages_spec}")
async def search(
    search_term: str,
    search_language_spec: str,
    translation_languages_spec: str = "",
    g: Graph = Depends(graph),
):
    """
    Search for the given term in the Quran and return the ayas containing the term.
    """

    search_results = []

    language, text_type = search_language_spec.split(":", 1)
    language_translations = []

    for lang in translation_languages_spec.split("_"):
        language_translations.append(lang.split(":", 1))

    if not search_term:
        return search_results

    log.info(
        f"Searching for term: '{search_term}' in language: {language}, text_type: {text_type}"
    )

    # Find ayas matching the search term via their text
    matched = g.cypher(
        "MATCH (a:Aya)-[e:AYA_TEXT]->(t:Text) "
        "WHERE e.language = $lang AND e.text_type = $tt AND t.text CONTAINS $term "
        "RETURN a.id, t.text",
        columns=["aya_id", "text"],
        lang=language,
        tt=text_type,
        term=search_term,
    )

    log.info(f"Found {len(matched)} aya matches")

    if not matched:
        return search_results

    # Build translation filter
    tr_parts = []
    tr_params = {}
    for idx, (tr_lang, tr_text_type) in enumerate(language_translations):
        tr_parts.append(f"(e.language = $tr_lang_{idx} AND e.text_type = $tr_tt_{idx})")
        tr_params[f"tr_lang_{idx}"] = tr_lang
        tr_params[f"tr_tt_{idx}"] = tr_text_type

    for m in matched:
        aya_key = m["aya_id"]
        search_result = {
            "aya_key": aya_key,
            "texts": {language: {text_type: m["text"]}},
        }

        # Get translations if requested
        if language_translations and tr_parts:
            tr_filter = " OR ".join(tr_parts)

            tr_results = g.cypher(
                "MATCH (a:Aya)-[e:AYA_TEXT]->(t:Text) "
                f"WHERE a.id = $aya_id AND ({tr_filter}) "
                "RETURN e.language, e.text_type, t.text",
                columns=["language", "text_type", "text"],
                aya_id=aya_key,
                **tr_params,
            )

            for tr in tr_results:
                if tr["language"] not in search_result["texts"]:
                    search_result["texts"][tr["language"]] = {}
                search_result["texts"][tr["language"]][tr["text_type"]] = tr["text"]

        search_results.append(search_result)

    return search_results
