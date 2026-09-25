"""Word morphology API: per-aya tokens, lemmas, roots."""

from collections import Counter, defaultdict

from age_orm import Graph
from fastapi import APIRouter, Depends, HTTPException, status

from .db import graph
from .schemas import (
    LemmaMeaningSchema,
    LemmaOccurrenceSchema,
    LemmaSchema,
    RootLemmaSchema,
    RootSchema,
    TokenSchema,
    WordMorphologySchema,
)

router = APIRouter(tags=["words"])

_TOKEN_COLUMNS = [
    "position",
    "text",
    "text_simple",
    "tag",
    "root",
    "lemma",
    "features",
    "segments",
    "glosses",
]


def _scalar(value):
    """age-orm returns {} for a null agtype scalar; map that to None."""
    return None if value == {} else value


def _clean(row: dict, fields: tuple[str, ...]) -> dict:
    return {k: (_scalar(v) if k in fields else v) for k, v in row.items()}


_TOKEN_SCALARS = ("text_simple", "tag", "root", "lemma", "features")


def _token_key(aya_key: str, position: int) -> tuple[int, int, int]:
    surah, aya = aya_key.split(":", 1)
    return int(surah), int(aya), position


@router.get("/aya-words/{aya_key}")
def get_aya_words(aya_key: str, g: Graph = Depends(graph)) -> list[TokenSchema]:
    """Words of one aya in reading order, with morphology and per-occurrence glosses."""
    rows = g.cypher(
        "MATCH (a:Aya {id: $aya})-[:HAS_TOKEN]->(t:Token) "
        "RETURN t.position, t.text, t.text_simple, t.tag, t.root, t.lemma, "
        "t.features, t.segments, t.glosses",
        columns=_TOKEN_COLUMNS,
        aya=aya_key,
    )
    rows.sort(key=lambda r: r["position"])
    return [TokenSchema(**_clean(r, _TOKEN_SCALARS)) for r in rows]


@router.get("/lemma/{lemma}")
def get_lemma(lemma: str, text_type: str = "simple", g: Graph = Depends(graph)) -> LemmaSchema:
    """A lemma with every occurrence (and the aya's Arabic text in the given text type)
    and the meanings used across those occurrences."""
    rows = g.cypher(
        "MATCH (a:Aya)-[:HAS_TOKEN]->(t:Token)-[:HAS_LEMMA]->(l:Lemma {id: $lemma}) "
        "OPTIONAL MATCH (a)-[e:AYA_TEXT]->(x:Text) "
        "WHERE e.language = 'arabic' AND e.text_type = $text_type "
        "RETURN l.pos, l.root, t.id, t.position, t.text, t.text_simple, t.glosses, x.text",
        columns=[
            "pos",
            "root",
            "token_id",
            "position",
            "text",
            "text_simple",
            "glosses",
            "aya_text",
        ],
        lemma=lemma,
        text_type=text_type,
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lemma not found")

    rows = [_clean(r, ("pos", "root", "text_simple", "aya_text")) for r in rows]
    occurrences = []
    gloss_counts: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        aya_key = r["token_id"].rsplit(":", 1)[0]
        glosses = r["glosses"] or {}
        occurrences.append(
            LemmaOccurrenceSchema(
                aya_key=aya_key,
                position=r["position"],
                text=r["text"],
                text_simple=r["text_simple"] or "",
                glosses=glosses,
                aya_text=r["aya_text"] or "",
            )
        )
        for language, gloss in glosses.items():
            gloss_counts[language][gloss] += 1
    occurrences.sort(key=lambda o: _token_key(o.aya_key, o.position))

    meanings = {
        language: [
            LemmaMeaningSchema(gloss=gloss, count=count) for gloss, count in counts.most_common()
        ]
        for language, counts in gloss_counts.items()
    }
    return LemmaSchema(
        lemma=lemma,
        pos=rows[0]["pos"],
        root=rows[0]["root"],
        count=len(occurrences),
        meanings=meanings,
        occurrences=occurrences,
    )


@router.get("/root/{root}")
def get_root(root: str, g: Graph = Depends(graph)) -> RootSchema:
    """A root with its lemmas and how often each occurs."""
    rows = g.cypher(
        "MATCH (l:Lemma)-[:HAS_ROOT]->(r:Root {id: $root}) "
        "OPTIONAL MATCH (t:Token)-[:HAS_LEMMA]->(l) "
        "RETURN r.letters, l.id, l.pos, count(t)",
        columns=["letters", "lemma", "pos", "count"],
        root=root,
    )
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Root not found")
    rows = [_clean(r, ("lemma", "pos")) for r in rows]
    lemmas = [RootLemmaSchema(lemma=r["lemma"], pos=r["pos"], count=r["count"]) for r in rows]
    lemmas.sort(key=lambda x: (-x.count, x.lemma))
    return RootSchema(
        root=root,
        letters=rows[0]["letters"],
        count=sum(x.count for x in lemmas),
        lemmas=lemmas,
    )


@router.get("/roots-by-letter/{letter}")
def get_roots_by_letter(letter: str, g: Graph = Depends(graph)) -> list[tuple[str, int]]:
    """Roots starting with the given letter, with their total occurrence counts."""
    rows = g.cypher(
        "MATCH (r:Root) WHERE left(r.id, 1) = $letter "
        "OPTIONAL MATCH (r)<-[:HAS_ROOT]-(:Lemma)<-[:HAS_LEMMA]-(t:Token) "
        "RETURN r.id, count(t)",
        columns=["root", "count"],
        letter=letter,
    )
    rows.sort(key=lambda r: r["root"])
    return [(r["root"], r["count"]) for r in rows]


@router.get("/word-morphology/{word}")
def get_word_morphology(word: str, g: Graph = Depends(graph)) -> list[WordMorphologySchema]:
    """Lemmas and roots behind a simple-text word form, with occurrence counts."""
    rows = g.cypher(
        "MATCH (w:Word {word: $word})<-[:IS_FORM]-(t:Token) "
        "OPTIONAL MATCH (t)-[:HAS_LEMMA]->(l:Lemma) "
        "RETURN l.id, l.root, l.pos, count(t)",
        columns=["lemma", "root", "pos", "count"],
        word=word,
    )
    rows = [_clean(r, ("lemma", "root", "pos")) for r in rows]
    result = [
        WordMorphologySchema(lemma=r["lemma"], root=r["root"], pos=r["pos"], count=r["count"])
        for r in rows
    ]
    result.sort(key=lambda x: (-x.count, x.lemma or ""))
    return result
