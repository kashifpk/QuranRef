import typer
from rich import print

from ..db import db as get_db
from ..models import Aya, Has, MetaInfo, QuranGraph, Surah, Text, Word

app = typer.Typer(name="Data post processing after import(s)")


@app.command(name="link-ayas-to-surahs")
def link_ayas_to_surahs():
    "Link Ayas to Surahs"

    db = get_db()

    qgraph = QuranGraph(connection=db)

    surahs = db.query(Surah).all()
    for surah in surahs:
        ayas = db.query(Aya).filter_by(surah_key=surah.key_).all()
        for aya in ayas:
            has_key = f"SA:{surah._key}:{aya._key}"
            has_document = qgraph.relation(surah, Has(_key=has_key), aya)
            _ = db.add(has_document, if_present="update")

    print("[green]Done![/green]")


@app.command(name="make-words")
def make_words():
    "Extract words from Ayas and store them in the database"

    db = get_db()

    qgraph = QuranGraph(connection=db)

    ayas = db.query(Aya).all()
    for aya in ayas:
        if 0 == aya.aya_number:
            continue

        aql = f"""
        FOR v, e, p IN 1..2 OUTBOUND 'ayas/{aya._key}' GRAPH 'quran_graph'
            FILTER p.edges[0].text_type=="simple-clean"
        RETURN p
        """

        obj = qgraph.aql(aql)

        print("Processing Aya:", aya._key)

        aya_text = obj._relations["aya_texts"][0]._next.text
        aya_words = aya_text.split(" ")
        # log.debug(aya_words)

        for word in aya_words:
            # add word with count=1 if it doesn't already exist, otherwise increment count
            word_doc = Word.new(db, word=word, count=1)
            if not db.exists(word_doc):
                db.add(word_doc)

            else:
                # log.debug(" --> Document exists")
                word_doc = db.query(Word).by_key(word_doc._key)
                word_doc.count += 1
                db.update(word_doc)

            # Aya linkage
            has_key = f"AW:{aya._key}:{word_doc._key}"
            has_document = qgraph.relation(aya, Has(_key=has_key), word_doc)
            _ = db.add(has_document, if_present="ignore")

    print("[green]Done![/green]")


@app.command(name="update-meta-info")
def update_meta_info():
    "Update MetaInfo collection with the latest data"

    db = get_db()

    ### Languages and text types
    arabic_texts_aql = """
    FOR doc IN aya_texts
    RETURN DISTINCT {language: doc.language, text_type: doc.text_type}
    """
    text_types = {}
    res = db.aql.execute(arabic_texts_aql)
    for r in res:
        if r["language"] not in text_types:
            text_types[r["language"]] = []

        text_types[r["language"]].append(r["text_type"])

    text_types_doc = MetaInfo(key_="text-types", value=text_types)
    _ = db.add(text_types_doc, if_present="update")

    print("[green]Text types updated![/green]")


@app.command(name="remove-bismillah")
def remove_bismillah():
    "Remove bismillah from the arabic of first aya of each Surah"

    db = get_db()

    bismillah_text = ""
    current_surah = ""

    db = get_db()
    quran_graph = QuranGraph(connection=db)

    rec = db.query(MetaInfo).by_key("text-types")
    arabic_text_types = rec.value["arabic"]

    for arabic_text_type in arabic_text_types:
        # Get bismillah text from aya 1:1 and then strip it from first aya of all other surahs
        first_aya = db.query(Aya).by_key("1:1")
        quran_graph.expand(
            first_aya,
            "any",
            1,
            only=[Text],
            condition=f"path.edges[0].language=='arabic' && path.edges[0].text_type=='{arabic_text_type}'",
        )

        bismillah_text = first_aya._relations['aya_texts'][0]._next.text

        # Now get first aya of surahs 2 to 114 and remove bismillah from them
        for surah_number in range(2, 115):
            aya_key = f"{surah_number}:1"
            aya = db.query(Aya).by_key(aya_key)
            quran_graph.expand(
                aya,
                "any",
                1,
                only=[Text],
                condition=f"path.edges[0].language=='arabic' && path.edges[0].text_type=='{arabic_text_type}'",
            )

            aya_text = aya._relations['aya_texts'][0]._next.text
            if aya_text.startswith(bismillah_text):
                print(f"Removing bismillah from surah {surah_number}, aya: 1, {aya_text}")
                aya_text = aya_text[len(bismillah_text):].strip()
                aya_text_doc = aya._relations['aya_texts'][0]._next
                aya_text_doc.text = aya_text
                db.update(aya_text_doc)

    # for line in fp:
    #     # Translations from tanzil.net contain a copyright block at the end which is separted
    #     # by 2 empty lines. We exit the loop when we encounter an empty line to avoid processing
    #     # that block a Quran text
    #     if not line.strip():
    #         break

    #     surah, aya, content = line.split('|', 2)
    #     content = content.strip()

    #     if not bismillah_text:
    #         bismillah_text = content

    #     if current_surah != surah:
    #         current_surah = surah
    #         if content.startswith(bismillah_text):
    #             if content[len(bismillah_text):].strip():
    #                 # new surah starting, separate bismillah and save as aya 0 for surah if first
    #                 # aya is not just bismillah
    #                 bismillah_aya_doc = Aya.get_or_new(db, surah_number=int(surah), aya_number=0)
    #                 AyaText.new(db, bismillah_aya_doc, bismillah_text, language, text_name)

    #                 content = content[len(bismillah_text):].strip()

    #     if content:
    #         aya_doc = Aya.get_or_new(db, surah_number=int(surah), aya_number=int(aya))
    #         AyaText.new(db, aya_doc, content, language, text_name)
