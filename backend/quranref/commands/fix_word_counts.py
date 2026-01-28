"""Fix word counts by recalculating from actual aya edges."""

import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..db import db as get_db


def fix_word_counts():
    """Recalculate word counts from actual aya-word edges."""

    db = get_db()

    print("[yellow]Recalculating word counts from edges...[/yellow]")

    # Get count of edges per word
    aql = """
    FOR e IN has
        FILTER STARTS_WITH(e._to, 'words/')
        COLLECT word_id = e._to WITH COUNT INTO edge_count
        RETURN {word_id: word_id, count: edge_count}
    """

    edge_counts = {r['word_id']: r['count'] for r in db.aql.execute(aql)}
    print(f"[blue]Found {len(edge_counts)} words with edges[/blue]")

    # Get all words
    words = list(db.aql.execute("FOR doc IN words RETURN doc"))
    print(f"[blue]Total words in collection: {len(words)}[/blue]")

    fixed_count = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Fixing counts...", total=len(words))

        for word_doc in words:
            word_id = word_doc['_id']
            current_count = word_doc.get('count', 0)
            actual_count = edge_counts.get(word_id, 0)

            if current_count != actual_count:
                # Update the word count
                db.aql.execute(
                    "UPDATE @key WITH {count: @count} IN words",
                    bind_vars={'key': word_doc['_key'], 'count': actual_count}
                )
                fixed_count += 1

            progress.advance(task)

    print(f"[green]Fixed {fixed_count} word counts![/green]")

    # Verify with a sample
    print("\n[yellow]Verification sample:[/yellow]")
    sample_aql = """
    FOR doc IN words
        FILTER doc.word == 'كاشف'
        RETURN {word: doc.word, count: doc.count}
    """
    for r in db.aql.execute(sample_aql):
        print(f"  {r}")


if __name__ == "__main__":
    fix_word_counts()
