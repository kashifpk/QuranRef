import logging

from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from arango_orm.exceptions import DocumentNotFoundError
from arango_orm import Database

from . import API_BASE
from .settings import get_settings
from .db import db
from .models import Surah, Aya, Word, QuranGraph, Has, MetaInfo

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
async def get_surahs(db: Database = Depends(db)) -> list[Surah]:
    """
    Get all Surahs
    """
    # results = {}

    surahs: list[Surah] = db.query(Surah).all()
    # for surah in surahs:
    #     breakpoint()
    #     results[surah.key_] = surah.model_dump()

    return surahs


@router.get("/text-types")
async def get_text_types(db: Database = Depends(db)) -> dict[str, list[str]]:
    """
    Get all text types
    """
    rec = db.query(MetaInfo).by_key("text-types")
    return rec.value


@router.get("/words-by-letter/{arabic_letter}")
async def get_words_by_letter(
    arabic_letter: str, db: Database = Depends(db)
) -> list[tuple[str, int]]:
    """
    Get all words starting with the given Arabic letter
    """
    aql = f"""
    FOR doc IN words
        FILTER LEFT(doc.word, 1)=='{arabic_letter}'
        SORT doc.word
    RETURN doc
    """

    results = [(r["word"], r["count"]) for r in db.aql.execute(aql)]

    return results


def _process_aya_results(obj) -> list:
    ayas = []
    for rel in obj._relations["has"]:
        d = {"aya_number": rel._next._key, "texts": {}}
        for aya_text in rel._next._relations["aya_texts"]:
            if aya_text.language not in d["texts"]:
                d["texts"][aya_text.language] = {}

            d["texts"][aya_text.language][aya_text.text_type] = aya_text._next.text

        ayas.append(d)

    return ayas


@router.get("/ayas-by-word/{word}/{languages}")
async def get_ayas_by_word(word: str, languages: str, db: Database = Depends(db)) -> list[dict]:
    """
    Get all ayas containing the given word and return text in the given languages and
    specific translator. Language items are separated by underscore while within a
    language item there is the language name and it's text type/translation separated by
    colon.

    For example:
        arabic:simple means arabic content with simple syntax.
        urdu:maududi returns urdu translations by Maududi

    .. code-block:: shell

        curl -XGET -H "Content-Type: application/json" \\
            "http://quranref.info/api/v1/ayas-by-word/عابد/arabic:simple_urdu:maududi_english:maududi"
    """
    word_doc = db.query(Word).filter_by(word=word).first()
    if word_doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Word not found")

    aql = f"FOR v, e, p IN 1..2 ANY '{word_doc.id_}' GRAPH '{QuranGraph.__graph__}'\n"
    aql += "FILTER "

    for lang in languages.split("_"):
        language, text_type = lang.split(":")
        aql += f'(e.language=="{language}" AND e.text_type=="{text_type}") OR '

    aql = aql.strip(" OR ")
    aql += "\nRETURN p"

    log.debug(aql)

    qgraph = QuranGraph(connection=db)

    obj = qgraph.aql(aql)
    if not obj:
        return []

    return _process_aya_results(obj)
