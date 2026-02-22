import bz2
import json
from pathlib import Path

import typer
from rich import print

from ..data.surah_info import surah_info
from ..db import get_db, graph as get_graph, GRAPH_NAME, raw_connection
from ..models import Aya, AyaText, HasAya, HasWord, Surah, Text, Word

app = typer.Typer(name="Database structure related operations")

META_INFO_DDL = """
CREATE TABLE IF NOT EXISTS meta_info (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL
)
"""


@app.command()
def init():
    "Create database graph, ensure labels, indexes, and meta_info table"

    db = get_db()
    g = db.graph(GRAPH_NAME, create=True)

    # Ensure all vertex and edge labels exist
    for vertex_cls in [Surah, Aya, Text, Word]:
        g.ensure_label(vertex_cls)
    for edge_cls in [HasAya, HasWord, AyaText]:
        g.ensure_label(edge_cls, kind="e")

    # Create indexes on key properties
    g.create_index(Surah, "id", unique=True)
    g.create_index(Aya, "id", unique=True)
    g.create_index(Aya, "surah_key")
    g.create_index(Text, "id", unique=True)
    g.create_index(Word, "id", unique=True)
    g.create_index(Word, "word")
    g.create_index(Word, "count")

    # Create meta_info SQL table
    with raw_connection() as conn:
        conn.execute(META_INFO_DDL)
        conn.commit()

    print("[green]Database initialization done.[/green]")


@app.command(name="populate-surahs")
def populate_surahs():
    "Populate Surahs"

    g = get_graph()

    surahs = []
    for idx, d_surah in enumerate(surah_info):
        surah = Surah(
            id=str(idx + 1),
            surah_number=idx + 1,
            arabic_name=d_surah["arabic_name"],
            english_name=d_surah["english_name"],
            translated_name=d_surah["translated_name"],
            nuzool_location=d_surah["nuzool_location"],
            nuzool_order=d_surah["nuzool_order"],
            rukus=d_surah["rukus"],
            total_ayas=d_surah["total_ayas"],
        )
        surahs.append(surah)

    g.bulk_add(surahs)
    print("[green]Surahs populated.[/green]")


@app.command(name="import-text")
def import_text(
    language: str,
    text_name: str,
    file_name: Path = typer.Argument(
        ...,
        help="Path to the file containing the text. Can be plain text or bzip2 compressed.",
        exists=True,
        dir_okay=False,
        file_okay=True,
        readable=True,
    ),
):
    "Import Arabic text or other language translations for Ayas"

    if file_name.suffix == ".bz2":
        fp = bz2.open(file_name, "rt")
    else:
        fp = open(file_name, "r")

    bismillah_text = ''
    current_surah = ''

    g = get_graph()

    for line in fp:
        if not line.strip():
            break

        surah, aya, content = line.split('|', 2)
        content = content.strip()

        if not bismillah_text:
            bismillah_text = content

        if current_surah != surah:
            current_surah = surah
            if content.startswith(bismillah_text):
                if content[len(bismillah_text):].strip():
                    bismillah_aya_doc = Aya.get_or_new(g, surah_number=int(surah), aya_number=0)
                    AyaText.new(g, bismillah_aya_doc, bismillah_text, language, text_name)

                    content = content[len(bismillah_text):].strip()

        if content:
            aya_doc = Aya.get_or_new(g, surah_number=int(surah), aya_number=int(aya))
            AyaText.new(g, aya_doc, content, language, text_name)

    fp.close()

    print(f"[green]{language}-{text_name} text imported.[/green]")


@app.command(name="import-json")
def import_json(
    data_dir: Path = typer.Argument(
        ...,
        help="Path to directory containing JSON export files.",
        exists=True,
        dir_okay=True,
        file_okay=False,
        readable=True,
    ),
):
    "Bulk import data from JSON exports (from ArangoDB migration)"

    g = get_graph()

    # 1. Import Surahs
    surahs_file = data_dir / "surahs.json"
    if surahs_file.exists():
        print("[blue]Importing surahs...[/blue]")
        with open(surahs_file) as f:
            surahs_data = json.load(f)
        surahs = [
            Surah(
                id=s["_key"],
                surah_number=s["surah_number"],
                arabic_name=s["arabic_name"],
                english_name=s["english_name"],
                translated_name=s["translated_name"],
                nuzool_location=s["nuzool_location"],
                nuzool_order=s["nuzool_order"],
                rukus=s["rukus"],
                total_ayas=s["total_ayas"],
            )
            for s in surahs_data
        ]
        g.bulk_add(surahs)
        print(f"[green]  {len(surahs)} surahs imported.[/green]")

    # 2. Import Ayas
    ayas_file = data_dir / "ayas.json"
    if ayas_file.exists():
        print("[blue]Importing ayas...[/blue]")
        with open(ayas_file) as f:
            ayas_data = json.load(f)
        ayas = [
            Aya(
                id=a["_key"],
                surah_key=a["surah_key"],
                aya_number=a["aya_number"],
            )
            for a in ayas_data
        ]
        g.bulk_add(ayas)
        print(f"[green]  {len(ayas)} ayas imported.[/green]")

    # 3. Import Texts
    texts_file = data_dir / "texts.json"
    if texts_file.exists():
        print("[blue]Importing texts...[/blue]")
        with open(texts_file) as f:
            texts_data = json.load(f)
        texts = [
            Text(id=t["_key"], text=t["text"])
            for t in texts_data
        ]
        g.bulk_add(texts)
        print(f"[green]  {len(texts)} texts imported.[/green]")

    # 4. Import Words
    words_file = data_dir / "words.json"
    if words_file.exists():
        print("[blue]Importing words...[/blue]")
        with open(words_file) as f:
            words_data = json.load(f)
        words = [
            Word(id=w["_key"], word=w["word"], count=w.get("count", 1))
            for w in words_data
        ]
        g.bulk_add(words)
        print(f"[green]  {len(words)} words imported.[/green]")

    # Build lookup maps for edge import (id string → graph_id)
    print("[blue]Building vertex lookup maps...[/blue]")
    surah_map = {s.id: s for s in g.query(Surah).all()}
    aya_map = {a.id: a for a in g.query(Aya).all()}
    text_map = {t.id: t for t in g.query(Text).all()}
    word_map = {w.id: w for w in g.query(Word).all()}

    # 5. Import HAS_AYA edges (Surah→Aya) and HAS_WORD edges (Aya→Word) from has_edges.json
    has_file = data_dir / "has_edges.json"
    if has_file.exists():
        print("[blue]Importing has edges (HAS_AYA + HAS_WORD)...[/blue]")
        with open(has_file) as f:
            has_data = json.load(f)

        has_aya_triples = []
        has_word_triples = []

        for e in has_data:
            from_col, from_key = e["_from"].split("/", 1)
            to_col, to_key = e["_to"].split("/", 1)

            if from_col == "surahs" and to_col == "ayas":
                surah = surah_map.get(from_key)
                aya = aya_map.get(to_key)
                if surah and aya:
                    has_aya_triples.append((surah, HasAya(), aya))
            elif from_col == "ayas" and to_col == "words":
                aya = aya_map.get(from_key)
                word = word_map.get(to_key)
                if aya and word:
                    has_word_triples.append((aya, HasWord(), word))

        if has_aya_triples:
            g.bulk_add_edges(has_aya_triples)
            print(f"[green]  {len(has_aya_triples)} HAS_AYA edges imported.[/green]")
        if has_word_triples:
            g.bulk_add_edges(has_word_triples)
            print(f"[green]  {len(has_word_triples)} HAS_WORD edges imported.[/green]")

    # 6. Import AYA_TEXT edges (Aya→Text)
    aya_texts_file = data_dir / "aya_texts_edges.json"
    if aya_texts_file.exists():
        print("[blue]Importing AYA_TEXT edges...[/blue]")
        with open(aya_texts_file) as f:
            aya_texts_data = json.load(f)

        aya_text_triples = []
        for e in aya_texts_data:
            _from_col, from_key = e["_from"].split("/", 1)
            _to_col, to_key = e["_to"].split("/", 1)

            aya = aya_map.get(from_key)
            text = text_map.get(to_key)
            if aya and text:
                edge = AyaText(language=e["language"], text_type=e["text_type"])
                aya_text_triples.append((aya, edge, text))

        if aya_text_triples:
            g.bulk_add_edges(aya_text_triples)
            print(f"[green]  {len(aya_text_triples)} AYA_TEXT edges imported.[/green]")

    # 7. Import meta_info
    meta_file = data_dir / "meta_info.json"
    if meta_file.exists():
        print("[blue]Importing meta_info...[/blue]")
        with open(meta_file) as f:
            meta_data = json.load(f)
        with raw_connection() as conn:
            for rec in meta_data:
                conn.execute(
                    "INSERT INTO meta_info (key, value) VALUES (%s, %s) "
                    "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                    (rec["_key"], json.dumps(rec["value"])),
                )
            conn.commit()
        print(f"[green]  {len(meta_data)} meta_info records imported.[/green]")

    print("[green]JSON import complete![/green]")
