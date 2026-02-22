"""Fix word counts by recalculating from actual aya edges."""

from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..db import graph as get_graph


def fix_word_counts():
    """Recalculate word counts from actual aya-word edges."""

    g = get_graph()

    print("[yellow]Recalculating word counts from edges...[/yellow]")

    # Get count of HAS_WORD edges per word using Cypher
    results = g.cypher(
        "MATCH (a:Aya)-[:HAS_WORD]->(w:Word) "
        "RETURN id(w) as word_gid, w.word as word, count(a) as edge_count",
        columns=["word_gid", "word", "edge_count"],
        return_type="raw",
    )

    edge_counts = {r["word_gid"]: r["edge_count"] for r in results}
    print(f"[blue]Found {len(edge_counts)} words with edges[/blue]")

    # Get all words
    from ..models import Word
    all_words = g.query(Word).all()
    print(f"[blue]Total words: {len(all_words)}[/blue]")

    fixed_count = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Fixing counts...", total=len(all_words))

        for word in all_words:
            actual_count = edge_counts.get(word.graph_id, 0)

            if word.count != actual_count:
                word.count = actual_count
                g.update(word)
                fixed_count += 1

            progress.advance(task)

    print(f"[green]Fixed {fixed_count} word counts![/green]")

    # Verify with a sample
    print("\n[yellow]Verification sample:[/yellow]")
    sample = g.cypher(
        "MATCH (w:Word) WHERE w.word = $word RETURN w.word, w.count",
        columns=["word", "count"],
        return_type="raw",
        word="كاشف",
    )
    for r in sample:
        print(f"  {r}")


if __name__ == "__main__":
    fix_word_counts()
