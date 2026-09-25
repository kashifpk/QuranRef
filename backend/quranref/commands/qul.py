"""Import QUL datasets: topics, ayah themes, similar ayahs, mutashabihat phrases."""

import json
import sqlite3
from pathlib import Path

import typer
from rich import print

from ..db import get_db
from ..db import graph as get_graph
from ..models import (
    Aya,
    ChildOf,
    HasPhrase,
    HasTheme,
    HasTopic,
    Phrase,
    RelatedTopic,
    SimilarTo,
    Theme,
    Topic,
)

app = typer.Typer(name="Import datasets from the Quranic Universal Library")


def _aya_map(g):
    return {a.id: a for a in g.query(Aya).all()}


def _bulk_edges(g, triples, batch=50_000):
    for start in range(0, len(triples), batch):
        g.bulk_add_edges(triples[start : start + batch])


@app.command(name="import-topics")
def import_topics(db_file: Path = typer.Argument(..., exists=True, help="QUL topics.db")):
    """Topics with their hierarchies, related topics and the ayas they cover. Replaces existing."""
    g = get_graph()
    g.cypher("MATCH (t:Topic) DETACH DELETE t")
    aya_map = _aya_map(g)

    conn = sqlite3.connect(db_file)
    rows = conn.execute(
        "SELECT topic_id, name, arabic_name, parent_id, thematic_parent_id, ontology_parent_id, "
        "description, wiki_link, thematic, ontology, ayahs, related_topics FROM topics"
    ).fetchall()

    topics: dict[str, Topic] = {}
    parents: list[tuple[str, str, str]] = []  # child, parent, kind
    related: list[tuple[str, str]] = []
    has_topic: list = []
    for (
        tid,
        name,
        arabic,
        parent,
        thematic_parent,
        ontology_parent,
        desc,
        wiki,
        them,
        onto,
        ayahs,
        rel,
    ) in rows:
        keys = [k.strip() for k in (ayahs or "").split(",") if k.strip() in aya_map]
        topics[str(tid)] = Topic(
            id=str(tid),
            name=name or "",
            arabic_name=arabic or "",
            description=desc or "",
            wiki_link=wiki or "",
            thematic=bool(them),
            ontology=bool(onto),
            aya_count=len(keys),
        )
        for kind, pid in (
            ("parent", parent),
            ("thematic", thematic_parent),
            ("ontology", ontology_parent),
        ):
            if pid is not None:
                parents.append((str(tid), str(pid), kind))
        for rid in (rel or "").split(","):
            if rid.strip():
                related.append((str(tid), rid.strip()))
        has_topic.extend((aya_map[k], str(tid)) for k in keys)

    g.bulk_add(list(topics.values()))
    _bulk_edges(g, [(topics[c], ChildOf(kind=k), topics[p]) for c, p, k in parents if p in topics])
    _bulk_edges(g, [(topics[a], RelatedTopic(), topics[b]) for a, b in related if b in topics])
    _bulk_edges(g, [(aya, HasTopic(), topics[t]) for aya, t in has_topic])
    print(
        f"[green]{len(topics)} topics, {len(parents)} hierarchy links, {len(has_topic)} aya links imported.[/green]"
    )


@app.command(name="import-themes")
def import_themes(db_file: Path = typer.Argument(..., exists=True, help="QUL ayah-themes.db")):
    """Ayah themes (aya ranges per surah). Replaces existing."""
    g = get_graph()
    g.cypher("MATCH (t:Theme) DETACH DELETE t")
    aya_map = _aya_map(g)
    conn = sqlite3.connect(db_file)
    rows = conn.execute(
        "SELECT rowid, theme, surah_number, ayah_from, ayah_to, keywords FROM themes"
    ).fetchall()
    themes = []
    edges = []
    seen: set[tuple] = set()
    for rowid, theme, surah, a_from, a_to, keywords in rows:
        key = ((theme or "").strip(), surah, a_from, a_to)
        if key in seen:  # the source has a few duplicated rows
            continue
        seen.add(key)
        t = Theme(
            id=f"theme:{rowid}",
            theme=theme or "",
            surah_number=surah,
            aya_from=a_from,
            aya_to=a_to,
            keywords=keywords or "",
        )
        themes.append(t)
        for n in range(a_from, a_to + 1):
            aya = aya_map.get(f"{surah}:{n}")
            if aya is not None:
                edges.append((aya, HasTheme(), t))
    g.bulk_add(themes)
    _bulk_edges(g, edges)
    print(f"[green]{len(themes)} themes, {len(edges)} aya links imported.[/green]")


@app.command(name="import-similar")
def import_similar(
    json_file: Path = typer.Argument(..., exists=True, help="QUL matching-ayah.json"),
):
    """Similar ayas with scores and matched word ranges. Replaces existing."""
    g = get_graph()
    g.cypher("MATCH ()-[s:SIMILAR_TO]->() DELETE s")
    aya_map = _aya_map(g)
    with open(json_file, encoding="utf-8") as fp:
        data = json.load(fp)
    edges = []
    for key, matches in data.items():
        source = aya_map.get(key)
        if source is None or not matches:
            continue
        for m in matches:
            target = aya_map.get(m.get("matched_ayah_key", ""))
            if target is None:
                continue
            edges.append(
                (
                    source,
                    SimilarTo(
                        score=int(m.get("score") or 0),
                        coverage=int(m.get("coverage") or 0),
                        matched_words=int(m.get("matched_words_count") or 0),
                        match_words=m.get("match_words") or [],
                    ),
                    target,
                )
            )
    _bulk_edges(g, edges)
    print(f"[green]{len(edges)} similarity links imported.[/green]")


@app.command(name="import-phrases")
def import_phrases(
    phrases_file: Path = typer.Argument(..., exists=True, help="QUL phrases.json (Mutashabihat)"),
):
    """Recurring phrases and the ayas containing them. Replaces existing."""
    g = get_graph()
    g.cypher("MATCH (p:Phrase) DETACH DELETE p")
    aya_map = _aya_map(g)
    tokens: dict[str, dict[int, str]] = {}
    for r in g.cypher(
        "MATCH (a:Aya)-[:HAS_TOKEN]->(t:Token) RETURN a.id, t.position, t.text",
        columns=["aya_key", "position", "text"],
    ):
        tokens.setdefault(r["aya_key"], {})[r["position"]] = r["text"]

    with open(phrases_file, encoding="utf-8") as fp:
        data = json.load(fp)
    phrases = []
    edges = []
    for pid, rec in data.items():
        src = rec.get("source") or {}
        key, w_from, w_to = src.get("key", ""), int(src.get("from") or 0), int(src.get("to") or 0)
        words = tokens.get(key, {})
        text = " ".join(words[i] for i in range(w_from, w_to + 1) if i in words)
        occurrences = rec.get("ayah") or {}
        phrase = Phrase(
            id=f"phrase:{pid}",
            text=text,
            source_aya=key,
            source_from=w_from,
            source_to=w_to,
            aya_count=len(occurrences),
        )
        phrases.append(phrase)
        for aya_key, ranges in occurrences.items():
            aya = aya_map.get(aya_key)
            if aya is not None:
                edges.append((aya, HasPhrase(ranges=ranges), phrase))
    g.bulk_add(phrases)
    _bulk_edges(g, edges)
    print(f"[green]{len(phrases)} phrases, {len(edges)} aya links imported.[/green]")


@app.command(name="import-all")
def import_all(directory: Path = typer.Argument(..., exists=True, file_okay=False)):
    """Run every importer against the files in a QUL download folder."""
    import_topics(directory / "topics.db")
    import_themes(directory / "ayah-themes.db")
    import_similar(directory / "matching-ayah.json")
    import_phrases(directory / "phrases.json")
    import_metadata(directory)


_UNITS = ("juz", "hizb", "rub", "manzil", "ruku")


def _expand(verse_mapping: dict) -> list[str]:
    """Aya keys covered by a QUL verse_mapping such as {"2": "1-141"}."""
    keys = []
    for surah, span in verse_mapping.items():
        first, _, last = span.partition("-")
        for n in range(int(first), int(last or first) + 1):
            keys.append(f"{surah}:{n}")
    return keys


@app.command(name="import-metadata")
def import_metadata(
    directory: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        help="Folder with quran-metadata-*.json and surah-info-*.json",
    ),
):
    """Juz, hizb, rub, manzil, ruku and sajda onto the ayas; the unit tables into
    meta_info; surah descriptions into surah_info."""
    from ..graph_bulk import set_vertex_properties

    g = get_graph()
    db = get_db()
    aya_map = _aya_map(g)

    updates: dict[str, dict] = {k: {} for k in aya_map}
    structure: dict[str, list] = {}
    for unit in _UNITS:
        with open(directory / f"quran-metadata-{unit}.json", encoding="utf-8") as fp:
            data = json.load(fp)
        entries = []
        for rec in data.values():
            number = int(rec[f"{unit}_number"])
            entries.append(
                {
                    "number": number,
                    "verses_count": rec.get("verses_count"),
                    "first_verse_key": rec.get("first_verse_key"),
                    "last_verse_key": rec.get("last_verse_key"),
                    "verse_mapping": rec.get("verse_mapping", {}),
                    **(
                        {"surah_ruku_number": rec.get("surah_ruku_number")}
                        if unit == "ruku"
                        else {}
                    ),
                }
            )
            for key in _expand(rec.get("verse_mapping", {})):
                if key in updates:
                    updates[key][unit] = number
                    if unit == "ruku":
                        updates[key]["surah_ruku"] = int(rec.get("surah_ruku_number") or 0)
        entries.sort(key=lambda e: e["number"])
        structure[unit] = entries

    with open(directory / "quran-metadata-sajda.json", encoding="utf-8") as fp:
        for rec in json.load(fp).values():
            if rec.get("verse_key") in updates:
                updates[rec["verse_key"]]["sajda"] = rec.get("sajdah_type")

    updates = {k: v for k, v in updates.items() if v}
    updated = set_vertex_properties(g, db, "Aya", updates)
    print(f"[green]{updated} ayas updated with mushaf structure.[/green]")

    with db._pool.connection() as conn:
        conn.execute(
            "INSERT INTO meta_info (key, value) VALUES (%s, %s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            ("structure", json.dumps(structure)),
        )
        rows = 0
        for language, suffix in (("english", "en"), ("urdu", "ur")):
            path = directory / f"surah-info-{suffix}.json"
            if not path.exists():
                continue
            with open(path, encoding="utf-8") as fp:
                for rec in json.load(fp).values():
                    conn.execute(
                        "INSERT INTO surah_info (surah_number, language, text, short_text) "
                        "VALUES (%s, %s, %s, %s) ON CONFLICT (surah_number, language) "
                        "DO UPDATE SET text = EXCLUDED.text, short_text = EXCLUDED.short_text",
                        (
                            int(rec["surah_number"]),
                            language,
                            rec.get("text") or "",
                            rec.get("short_text") or "",
                        ),
                    )
                    rows += 1
        conn.commit()
    print(f"[green]Structure stored; {rows} surah descriptions imported.[/green]")
