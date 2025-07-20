import logging

from arango_orm import Database
from fastapi import APIRouter, Depends, HTTPException, status

from .db import db
from .models import MetaInfo, QuranGraph, Surah, Text, Word
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


def _process_aya_results(obj) -> list[AyaResultSchema]:
    ayas = []
    for rel in obj._relations["has"]:
        d = AyaResultSchema(aya_key=rel._next._key, texts={})
        for aya_text in rel._next._relations["aya_texts"]:
            if aya_text.language not in d.texts:
                d.texts[aya_text.language] = {}

            d.texts[aya_text.language][aya_text.text_type] = aya_text._next.text

        ayas.append(d)

    return ayas


@router.get("/ayas-by-word/{word}/{languages}")
async def get_ayas_by_word(
    word: str, languages: str, db: Database = Depends(db)
) -> list[AyaResultSchema]:
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


@router.get("/words-by-count/{count}")
async def get_words_by_count(count: int, db: Database = Depends(db)) -> list[str]:
    """
    Get all words with the given count
    """
    words = db.query(Word).filter_by(count=count).sort("word")
    result = [word.word for word in words.iterator()]

    return result


@router.get("/top-most-frequent-words/{limit}")
async def get_top_most_frequent_words(
    limit: int, db: Database = Depends(db)
) -> list[tuple[str, int]]:
    """
    Get top most frequent words
    """
    aql = f"""
    FOR doc IN words
        SORT doc.count DESC, doc.word
        LIMIT {limit}
    RETURN doc
    """

    results = [(r["word"], r["count"]) for r in db.aql.execute(aql)]

    return results


@router.get("/top-least-frequent-words/{limit}")
async def get_top_least_frequent_words(
    limit: int, db: Database = Depends(db)
) -> list[tuple[str, int]]:
    """
    Get top least frequent words
    """
    aql = f"""
    FOR doc IN words
        SORT doc.count ASC, doc.word
        LIMIT {limit}
    RETURN doc
    """

    results = [(r["word"], r["count"]) for r in db.aql.execute(aql)]

    return results


@router.get("/text/{ayas_spec}/{languages_spec}")
async def get_text(
    ayas_spec: str, languages_spec: str, db: Database = Depends(db)
) -> list[AyaResultSchema]:
    """
    Get text for the given ayas and languages.

    :param ayas_spec: Aya specification. Can have different formats.

        surah - When it's only a single number, it's considered to be
        the surah number. For example `114` means all ayas of Surah 114.

        surah:aya - When it's in the format surah:aya, it's considered a single aya.
        For example `114:1` means Surah 114, Aya 1.

        surah:aya1-aya2 - When it's in the format surah:aya1-aya2, it's considered a range
        of ayas. For example `99:4-16` means Surah 19, Ayas 4 to 16.

        For performance reasons fetching multiple surahs or aya ranges that span multiple surahs
        is not supported. So spec like `2-10`, `2:1-3:10` are invalid.

    :param languages_spec: Language specification.

        Can have multiple language specification items.

        Each language specification item is in the format language:text-type. For example
        `arabic:simple`, `urdu:maududi`, `english:ahmed-ali`.

        Multiple language specification items are separated by underscore. For example
        `arabic:simple_urdu:maududi_english:ahmed-ali`.
    """

    surah_number = None
    aya_num_or_range = None

    if "-" not in ayas_spec and ":" not in ayas_spec:
        # Only surah number is given
        surah_number = ayas_spec
    else:
        # Surah and aya number/range is given
        surah_number, aya_num_or_range = ayas_spec.split(":", 1)

    if surah_number is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid surah number")

    aql = f"FOR v, e, p IN 1..2 OUTBOUND 'surahs/{surah_number}' GRAPH 'quran_graph'\n"

    # Add aya filter
    if aya_num_or_range is not None:
        if "-" in aya_num_or_range:
            start_aya, end_aya = aya_num_or_range.split("-", 1)

            aql += (
                f"FILTER p['vertices'][1].aya_number>={start_aya} "
                f"AND p['vertices'][1].aya_number<={end_aya}\n"
            )
        else:
            aql += f"FILTER p['vertices'][1].aya_number=={aya_num_or_range}\n"

    # Add language and text_type filters
    # `arabic:simple_urdu:maududi_english:ahmed-ali`
    aql += "FILTER "
    for lang in languages_spec.split("_"):
        language, text_type = lang.split(":")

        aql += f'(e.language=="{language}" && e.text_type=="{text_type}") OR '

    aql = aql.strip(" OR ")
    aql += "\nSORT p['vertices'][1].aya_number\nRETURN p"

    # print(aql)

    qgraph = QuranGraph(connection=db)
    obj = qgraph.aql(aql)
    # log.debug(obj._relations)
    return _process_aya_results(obj)


@router.get("/search/{search_term}/{search_language_spec}/{translation_languages_spec}")
async def search(
    search_term: str,
    search_language_spec: str,
    translation_languages_spec: str = "",
    db: Database = Depends(db),
):
    """
    Search for the given term in the Quran and return the ayas containing the term.

    :param search_term: Search term
    :param search_language_spec: Language specification for the language to search the text in.

        Format" language:text-type. For example `arabic:simple-clean`, `urdu:maududi`, `english:ahmed-ali`.

    :param translation_languages_spec: Translation language specification.

        Can have multiple language specification items.

        Each language specification item is in the format language:text-type. For example
        `urdu:maududi`, `english:ahmed-ali`.

        Multiple language specification items are separated by underscore. For example
        `urdu:maududi_english:ahmed-ali`.

    """

    # aarab = ["ِ", "ْ", "َ", "ُ", "ّ", "ٍ", "ً", "ٌ"]

    search_results = []
    # cleaned_search_term = ""

    # if search_language_spec == "arabic:simple-clean":
    #     for ch in search_term:
    #         if ch not in aarab:
    #             cleaned_search_term += ch
    # else:
    #     cleaned_search_term = search_term

    language, text_type = search_language_spec.split(":", 1)
    language_translations = []

    for lang in translation_languages_spec.split("_"):
        language_translations.append(lang.split(":", 1))

    tr_aql = ""
    for tr_lang_tuple in language_translations:
        tr_lang, tr_text_type = tr_lang_tuple
        tr_aql += f'(e.language=="{tr_lang}" && e.text_type=="{tr_text_type}") OR '

    tr_aql = tr_aql.strip(" OR ")

    if search_term:
        qgraph = QuranGraph(connection=db)
        log.info(f"Searching for term: '{search_term}' in language: {language}, text_type: {text_type}")
        
        # Simpler approach: Add filter for language/text_type to reduce search scope
        matched_texts = (
            db.query(Text)
            .filter(f"LIKE(rec.text, '%{search_term}%')", prepend_rec_name=False)
            .limit(1000)  # Add limit to prevent runaway queries
            .all()
        )
        
        log.info(f"Found {len(matched_texts)} text matches")
        
        if matched_texts:
            # Batch process: collect all matching text IDs and search in one query
            text_ids = [mt._key for mt in matched_texts]
            text_ids_str = "'" + "', '".join(text_ids) + "'"
            
            # Single AQL query to find all matching ayas
            batch_aql = f"""
            FOR text_id IN [{text_ids_str}]
                FOR v, e, p IN 1..1 INBOUND CONCAT('texts/', text_id) GRAPH 'quran_graph'
                    FILTER e.language == '{language}' AND e.text_type == '{text_type}'
                    RETURN {{
                        aya_key: v._key,
                        text_id: text_id
                    }}
            """
            
            batch_results = list(db.aql.execute(batch_aql))
            log.info(f"Found {len(batch_results)} aya matches after filtering")
            
            # Create a map of text_id to text content for quick lookup
            text_map = {mt._key: mt.text for mt in matched_texts}
            
            # Process unique ayas
            processed_ayas = set()
            
            for result in batch_results:
                aya_key = result["aya_key"]
                text_id = result["text_id"]
                
                if aya_key in processed_ayas:
                    continue
                processed_ayas.add(aya_key)
                
                search_result = {
                    "aya_key": aya_key,
                    "texts": {language: {text_type: text_map[text_id]}},
                }
                
                # Get translations if requested
                if language_translations:
                    aql = f"FOR v, e, p IN 1..2 OUTBOUND 'ayas/{aya_key}' GRAPH 'quran_graph'\n"
                    aql += f"FILTER {tr_aql}\n"
                    aql += "RETURN p"
                    
                    aya_obj = qgraph.aql(aql)
                    
                    if aya_obj and hasattr(aya_obj, '_relations') and 'aya_texts' in aya_obj._relations:
                        for aya_text in aya_obj._relations["aya_texts"]:
                            if aya_text.language not in search_result["texts"]:
                                search_result["texts"][aya_text.language] = {}
                            
                            search_result["texts"][aya_text.language][aya_text.text_type] = (
                                aya_text._next.text
                            )
                
                search_results.append(search_result)

    return search_results
