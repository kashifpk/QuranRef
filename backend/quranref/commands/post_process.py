import json

import typer
from rich import print

from ..db import graph as get_graph, raw_connection
from ..models import Aya, AyaText, HasAya, HasWord, Surah, Text, Word
from ..utils import text_to_digest

app = typer.Typer(name="Data post processing after import(s)")


@app.command(name="link-ayas-to-surahs")
def link_ayas_to_surahs():
    "Link Ayas to Surahs via HAS_AYA edges"

    g = get_graph()

    surahs = g.query(Surah).all()
    for surah in surahs:
        ayas = g.query(Aya).filter_by(surah_key=surah.id).all()
        triples = [(surah, HasAya(), aya) for aya in ayas]
        if triples:
            g.bulk_add_edges(triples)

    print("[green]Done![/green]")


@app.command(name="make-words")
def make_words():
    """Extract words from Ayas and store them in the database.

    This command is idempotent - running it multiple times will produce
    the same result. It clears existing word data before rebuilding.
    """

    g = get_graph()

    # Clear existing word-related data to ensure idempotency
    print("[yellow]Clearing existing word data for clean rebuild...[/yellow]")

    # Remove all HAS_WORD edges
    g.cypher("MATCH ()-[e:HAS_WORD]->() DELETE e")

    # Remove all Word vertices
    g.cypher("MATCH (w:Word) DELETE w")

    print("[blue]Extracting words from ayas...[/blue]")

    ayas = g.query(Aya).all()
    word_counts: dict[str, int] = {}
    aya_words_map: dict[str, list[str]] = {}  # aya.id -> list of word hashes

    for aya in ayas:
        if aya.aya_number == 0:
            continue

        # Get simple-clean text for this aya
        results = g.cypher(
            "MATCH (a:Aya)-[e:AYA_TEXT]->(t:Text) "
            "WHERE a.id = $aya_id AND e.text_type = $text_type "
            "RETURN t.text",
            columns=["text"],
            return_type="raw",
            aya_id=aya.id,
            text_type="simple-clean",
        )

        if not results:
            continue

        aya_text = results[0]["text"]
        print("Processing Aya:", aya.id)

        aya_word_hashes = []
        seen_in_aya: set[str] = set()
        for word_str in aya_text.split(" "):
            word_hash = text_to_digest(word_str)
            aya_word_hashes.append(word_hash)
            # Count each unique word once per aya (matches HAS_WORD edge semantics)
            if word_str not in seen_in_aya:
                seen_in_aya.add(word_str)
                word_counts[word_str] = word_counts.get(word_str, 0) + 1

        aya_words_map[aya.id] = aya_word_hashes

    # Bulk create word vertices
    print("[blue]Creating word vertices...[/blue]")
    word_objects = {}
    words_to_add = []
    for word_str, count in word_counts.items():
        w = Word.new(word=word_str, count=count)
        words_to_add.append(w)
        word_objects[text_to_digest(word_str)] = w

    g.bulk_add(words_to_add)

    # Bulk create HAS_WORD edges
    print("[blue]Creating HAS_WORD edges...[/blue]")
    aya_map = {a.id: a for a in ayas}
    edge_triples = []
    seen_edges: set[tuple[str, str]] = set()

    for aya_id, word_hashes in aya_words_map.items():
        aya = aya_map[aya_id]
        for wh in word_hashes:
            edge_key = (aya_id, wh)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                word_obj = word_objects[wh]
                edge_triples.append((aya, HasWord(), word_obj))

    if edge_triples:
        g.bulk_add_edges(edge_triples)

    print("[green]Done![/green]")


@app.command(name="update-meta-info")
def update_meta_info():
    "Update meta_info table with the latest data"

    g = get_graph()

    # Get all distinct language + text_type combinations from AYA_TEXT edges
    results = g.cypher(
        "MATCH ()-[e:AYA_TEXT]->() RETURN DISTINCT e.language, e.text_type",
        columns=["language", "text_type"],
        return_type="raw",
    )

    text_types: dict[str, list[str]] = {}
    for r in results:
        lang = r["language"]
        tt = r["text_type"]
        if lang not in text_types:
            text_types[lang] = []
        text_types[lang].append(tt)

    with raw_connection() as conn:
        conn.execute(
            "INSERT INTO meta_info (key, value) VALUES (%s, %s) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            ("text-types", json.dumps(text_types)),
        )
        conn.commit()

    print("[green]Text types updated![/green]")


@app.command(name="fix-word-counts")
def fix_word_counts_cmd():
    """Recalculate word counts from actual aya-word edges."""
    from .fix_word_counts import fix_word_counts as _fix
    _fix()


@app.command(name="remove-bismillah")
def remove_bismillah():
    "Remove bismillah from the arabic of first aya of each Surah"

    g = get_graph()

    # Get available arabic text types from meta_info
    with raw_connection() as conn:
        result = conn.execute(
            "SELECT value FROM meta_info WHERE key = %s", ("text-types",)
        ).fetchone()

    if not result:
        print("[red]No text-types found in meta_info. Run update-meta-info first.[/red]")
        return

    text_types_data = result[0] if isinstance(result[0], dict) else json.loads(result[0])
    arabic_text_types = text_types_data.get("arabic", [])

    for arabic_text_type in arabic_text_types:
        # Get bismillah text from aya 1:1
        results = g.cypher(
            "MATCH (a:Aya)-[e:AYA_TEXT]->(t:Text) "
            "WHERE a.id = $aya_id AND e.language = $lang AND e.text_type = $tt "
            "RETURN t.text, id(t) as text_gid",
            columns=["text", "text_gid"],
            return_type="raw",
            aya_id="1:1",
            lang="arabic",
            tt=arabic_text_type,
        )

        if not results:
            continue

        bismillah_text = results[0]["text"]

        # Process first aya of surahs 2 to 114
        for surah_number in range(2, 115):
            aya_key = f"{surah_number}:1"
            results = g.cypher(
                "MATCH (a:Aya)-[e:AYA_TEXT]->(t:Text) "
                "WHERE a.id = $aya_id AND e.language = $lang AND e.text_type = $tt "
                "RETURN t.text, id(t) as text_gid",
                columns=["text", "text_gid"],
                return_type="raw",
                aya_id=aya_key,
                lang="arabic",
                tt=arabic_text_type,
            )

            if not results:
                continue

            aya_text = results[0]["text"]
            text_gid = results[0]["text_gid"]

            if aya_text.startswith(bismillah_text):
                print(f"Removing bismillah from surah {surah_number}, aya: 1, {aya_text}")
                new_text = aya_text[len(bismillah_text):].strip()

                # Update the text vertex
                text_vertex = g.query(Text).by_id(text_gid)
                text_vertex.text = new_text
                g.update(text_vertex)

    print("[green]Done![/green]")
