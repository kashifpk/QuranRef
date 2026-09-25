import json
import logging

from age_orm import Graph
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from .ayatext import _build_language_filter, _process_aya_results, aya_sort_key
from .db import get_session, graph, raw_connection
from .models import Surah, Word
from .schemas import AyaResultSchema
from .sql_models import AyaSearch
from .textnorm import normalize_for_search

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/letters")
def get_letters() -> list[str]:
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
def get_surahs(g: Graph = Depends(graph)) -> list[Surah]:
    """
    Get all Surahs
    """
    surahs: list[Surah] = g.query(Surah).sort("n.surah_number").all()
    return surahs


@router.get("/text-types")
def get_text_types() -> dict[str, list[str]]:
    """
    Get all text types
    """
    with raw_connection() as conn:
        result = conn.execute(
            "SELECT value FROM meta_info WHERE key = %s", ("text-types",)
        ).fetchone()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Text types not found")

    value = result[0]
    if isinstance(value, str):
        value = json.loads(value)
    return value


@router.get("/words-by-letter/{arabic_letter}")
def get_words_by_letter(arabic_letter: str, g: Graph = Depends(graph)) -> list[tuple[str, int]]:
    """
    Get all words starting with the given Arabic letter
    """
    results = g.cypher(
        'MATCH (w:Word) WHERE left(w.word, 1) = $letter RETURN w.word, w["count"]',
        columns=["word", "count"],
        letter=arabic_letter,
    )

    results.sort(key=lambda r: r["word"])
    return [(r["word"], r["count"]) for r in results]


@router.get("/ayas-by-word/{word}/{languages}")
def get_ayas_by_word(word: str, languages: str, g: Graph = Depends(graph)) -> list[AyaResultSchema]:
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
def get_words_by_count(count: int, g: Graph = Depends(graph)) -> list[tuple[str, int]]:
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
def get_available_word_counts(g: Graph = Depends(graph)) -> list[dict]:
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
def get_top_most_frequent_words(limit: int, g: Graph = Depends(graph)) -> list[tuple[str, int]]:
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
def get_text(
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid surah number")

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


def _like_pattern(term: str) -> str:
    """Substring LIKE pattern for a normalized term, with LIKE wildcards escaped."""
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


@router.get("/search/{search_term}/{search_language_spec}/{translation_languages_spec}")
def search(
    search_term: str,
    search_language_spec: str,
    translation_languages_spec: str = "",
    session: Session = Depends(get_session),
) -> list[AyaResultSchema]:
    """
    Search for the given term and return the ayas containing it, with the matched text
    and the requested translations.

    Matching is done on the aya_search table, where both the stored text and the term
    are normalized (diacritics removed, letter variants folded, case folded), so
    searching for الله finds اللَّهِ and "merciful" finds "Merciful".
    """
    language, text_type = search_language_spec.split(":", 1)
    term = normalize_for_search(search_term)
    if not term:
        return []

    log.info(f"Searching for term: '{search_term}' in language: {language}, text_type: {text_type}")
    matched = session.execute(
        select(AyaSearch.aya_key, AyaSearch.text).where(
            AyaSearch.language == language,
            AyaSearch.text_type == text_type,
            AyaSearch.text_norm.like(_like_pattern(term), escape="\\"),
        )
    ).all()

    results: dict[str, AyaResultSchema] = {
        aya_key: AyaResultSchema(aya_key=aya_key, texts={language: {text_type: text}})
        for aya_key, text in matched
    }
    log.info(f"Found {len(results)} aya matches")

    pairs = [
        tuple(spec.split(":", 1)) for spec in translation_languages_spec.split("_") if ":" in spec
    ]
    if results and pairs:
        translations = session.execute(
            select(
                AyaSearch.aya_key, AyaSearch.language, AyaSearch.text_type, AyaSearch.text
            ).where(
                AyaSearch.aya_key.in_(list(results)),
                or_(
                    *[
                        and_(AyaSearch.language == lang, AyaSearch.text_type == tt)
                        for lang, tt in pairs
                    ]
                ),
            )
        ).all()
        for aya_key, lang, tt, text in translations:
            results[aya_key].texts.setdefault(lang, {})[tt] = text

    return sorted(results.values(), key=lambda a: aya_sort_key(a.aya_key))
