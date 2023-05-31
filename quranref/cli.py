import typer
from time import sleep
from .graph_models import get_gdb
from .graph_models.quran_graph import QuranGraph
from .graph_models.quran_graph import Surah
from .lib.surah_info import surah_info
from .graph_models.quran_graph import Aya, AyaText

cmd_app = typer.Typer()
"""
def iteration():
    for i in range(1000):
        yield i
"""

@cmd_app.command()
def populate():
    """Create database tables and graph."""
    print("Creating tables and graph")
    gdb = get_gdb()
    db_objects = [QuranGraph]
    gdb.create_all(db_objects)

@cmd_app.command()
def import_surahs():
    surah_number = 1
    for s_info in surah_info:
        s = Surah(
            _key=str(surah_number),
            surah_number=surah_number,
            arabic_name=s_info['arabic_name'],
            english_name=s_info['english_name'],
            translated_name=s_info['translated_name'],
            nuzool_location=s_info['nuzool_location'],
            nuzool_order=s_info['nuzool_order'],
            rukus=s_info['rukus'],
            total_ayas=s_info['total_ayas']
        )

        gdb = get_gdb()
        gdb.add(s)
        surah_number += 1


@cmd_app.command()
def import_text(language: str, text_name: str, filename: str):
    """
    with typer.progressbar(iteration(), length=1000, label="Progressing") as progress: 
        for i in progress:
            sleep(0.01)
    """
    file = open(filename)

    bismillah_text = ''
    current_surah = ''

    for line in file:
        if not line.strip():
            break

        surah, aya, content = line.split('|')

        if not bismillah_text:
            bismillah_text = content.strip()

        if current_surah != surah and content.startswith(bismillah_text):
            # new surah starting, separate bismillah and save as aya 0 for surah
            content = content[len(bismillah_text):].strip()
            if content:
                aya_doc = Aya.new(surah_number=surah, aya_number=0)
            else:
                aya_doc = Aya.new(surah_number=surah, aya_number=aya)

            AyaText.new(aya_doc, bismillah_text, language, text_name)
            current_surah = surah

        if content:
            aya_doc = Aya.new(surah_number=surah, aya_number=aya)
            AyaText.new(aya_doc, content.strip(), language, text_name)

@cmd_app.command()
def test():
    """A test command."""
    print("Hi, just testing")


def main():
    cmd_app()
