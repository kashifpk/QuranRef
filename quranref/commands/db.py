import bz2
from pathlib import Path

import typer
from arango_orm.exceptions import DocumentNotFoundError
from rich import print

from ..data.surah_info import surah_info
from ..db import db as get_db
from ..models import Aya, AyaText, Has, MetaInfo, QuranGraph, Surah, Text, Word

app = typer.Typer(name="Database structure related operations")


@app.command()
def init():
    "Create database collections and graph(s)"

    db = get_db()
    db.create_all([MetaInfo, QuranGraph])

    print("[green]Database initialization done.[/green]")


@app.command(name="populate-surahs")
def populate_surahs():
    "Populate Surahs collection"

    db = get_db()

    for idx, d_surah in enumerate(surah_info):
        surah = Surah(
            key_=str(idx + 1),
            surah_number=idx+1,
            arabic_name=d_surah["arabic_name"],
            english_name=d_surah["english_name"],
            translated_name=d_surah["translated_name"],
            nuzool_location=d_surah["nuzool_location"],
            nuzool_order=d_surah["nuzool_order"],
            rukus=d_surah["rukus"],
            total_ayas=d_surah["total_ayas"],
        )

        db.add(surah)

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

    db = get_db()

    for line in fp:
        # Translations from tanzil.net contain a copyright block at the end which is separted
        # by 2 empty lines. We exit the loop when we encounter an empty line to avoid processing
        # that block a Quran text
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
                    # new surah starting, separate bismillah and save as aya 0 for surah if first
                    # aya is not just bismillah
                    bismillah_aya_doc = Aya.get_or_new(db, surah_number=int(surah), aya_number=0)
                    AyaText.new(db, bismillah_aya_doc, bismillah_text, language, text_name)

                    content = content[len(bismillah_text):].strip()

        if content:
            aya_doc = Aya.get_or_new(db, surah_number=int(surah), aya_number=int(aya))
            AyaText.new(db, aya_doc, content, language, text_name)

    fp.close()

    print(f"[green]{language}-{text_name} text imported.[/green]")
