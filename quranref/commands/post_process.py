import typer
from rich import print

from ..db import db as get_db
from ..models import QuranGraph, Aya, Has, Word, MetaInfo


app = typer.Typer(name="Data post processing after import(s)")


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
        if r['language'] not in text_types:
            text_types[r['language']] = []

        text_types[r['language']].append(r['text_type'])

    text_types_doc = MetaInfo(key_='text-types', value=text_types)
    _ = db.add(text_types_doc, if_present="update")

    print("[green]Text types updated![/green]")
