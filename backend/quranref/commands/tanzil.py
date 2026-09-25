"""Check and refresh the Arabic texts and translations against tanzil.net."""

import time
from pathlib import Path

import typer
from rich import print
from rich.table import Table

from ..db import get_db
from ..db import graph as get_graph
from ..search_index import rebuild_search_index
from ..tanzil import (
    all_source_ids,
    apply_diff,
    diff_texts,
    download,
    graph_texts,
    parse_tanzil,
    prune_orphan_texts,
    read_bundled,
    same_text,
    source_name,
    split_bismillah,
    write_bundled,
)

app = typer.Typer(name="Tanzil texts and translations")


def _resolve(ids: list[str], all_sources: bool) -> list[str]:
    if all_sources:
        return all_source_ids()
    if not ids:
        raise typer.BadParameter("give one or more ids (en.sahih, quran:simple, ...) or --all")
    for source_id in ids:
        source_name(source_id)  # raises KeyError for unknown ids
    return ids


def _fresh_content(source_id: str, source_dir: Path | None, delay: float) -> str:
    if source_dir is not None:
        name = source_id.replace("quran:", "quran-")
        for candidate in (source_dir / f"{name}.txt", source_dir / name):
            if candidate.exists():
                return candidate.read_text(encoding="utf-8")
        raise FileNotFoundError(f"{name}.txt not found in {source_dir}")
    content = download(source_id)
    time.sleep(delay)
    return content


@app.command(name="list")
def list_sources():
    """The Tanzil ids this project knows and the graph names they map to."""
    table = Table("id", "language", "text_type", "bundled last update")
    for source_id in all_source_ids():
        language, text_type = source_name(source_id)
        bundled = read_bundled(source_id)
        meta = parse_tanzil(bundled).meta if bundled else {}
        table.add_row(
            source_id, language, text_type, meta.get("Last Update", meta.get("Version", ""))
        )
    print(table)


@app.command()
def check(
    ids: list[str] = typer.Argument(None, help="Tanzil ids, e.g. en.sahih or quran:simple"),
    all_sources: bool = typer.Option(False, "--all", help="Check every known source"),
    source_dir: Path | None = typer.Option(
        None, help="Read <id>.txt files from this folder instead of downloading"
    ),
    delay: float = typer.Option(1.0, help="Seconds to wait between downloads"),
):
    """Download the current files and report which ayas differ from the graph. No writes."""
    g = get_graph()
    for source_id in _resolve(ids or [], all_sources):
        language, text_type = source_name(source_id)
        fresh = parse_tanzil(_fresh_content(source_id, source_dir, delay))
        bundled_raw = read_bundled(source_id)
        bundled = parse_tanzil(bundled_raw) if bundled_raw else None
        diff = diff_texts(graph_texts(g, language, text_type), split_bismillah(fresh.ayas))
        file_state = (
            "no bundled copy"
            if bundled is None
            else (
                "bundled copy identical" if bundled.ayas == fresh.ayas else "bundled copy differs"
            )
        )
        state = (
            "[green]unchanged[/green]" if not diff else f"[yellow]{len(diff)} ayas differ[/yellow]"
        )
        cosmetic = len(diff.cosmetic())
        if cosmetic:
            state += f" ({cosmetic} only in combining-mark order)"
        print(
            f"{source_id:22s} {language}/{text_type}: {state} "
            f"({file_state}; Tanzil last update {fresh.meta.get('Last Update', 'n/a')})"
        )
        shown = 0
        for key, old, new in diff.changed:
            if same_text(old, new):
                continue
            print(f"    {key}: {old[:60]!r} -> {new[:60]!r}")
            shown += 1
            if shown == 5:
                break
        if diff.added:
            print(f"    added: {', '.join(diff.added[:10])}")
        if diff.removed:
            print(f"    removed: {', '.join(diff.removed[:10])}")


@app.command()
def refresh(
    ids: list[str] = typer.Argument(None, help="Tanzil ids, e.g. en.sahih or quran:simple"),
    all_sources: bool = typer.Option(False, "--all", help="Refresh every known source"),
    source_dir: Path | None = typer.Option(
        None, help="Read <id>.txt files from this folder instead of downloading"
    ),
    delay: float = typer.Option(1.0, help="Seconds to wait between downloads"),
    update_files: bool = typer.Option(True, help="Rewrite the bundled .txt.bz2 copies"),
    update_graph: bool = typer.Option(True, help="Apply changed ayas to the graph"),
):
    """Bring the bundled files and the graph up to date with tanzil.net.

    Rewrites a bundled copy when the download differs from it, replaces the changed ayas'
    texts in the graph, then prunes orphaned Text vertices and rebuilds the search index.
    """
    db = get_db()
    g = get_graph()
    graph_changes = 0
    files_written = 0
    for source_id in _resolve(ids or [], all_sources):
        language, text_type = source_name(source_id)
        content = _fresh_content(source_id, source_dir, delay)
        fresh = parse_tanzil(content)
        bundled_raw = read_bundled(source_id)
        bundled = parse_tanzil(bundled_raw) if bundled_raw else None
        if update_files and (bundled is None or bundled != fresh):
            write_bundled(source_id, content)
            files_written += 1
            print(f"{source_id}: bundled copy updated")
        if update_graph:
            texts = split_bismillah(fresh.ayas)
            diff = diff_texts(graph_texts(g, language, text_type), texts)
            if diff:
                apply_diff(g, language, text_type, texts, diff)
                graph_changes += len(diff)
                print(
                    f"{source_id}: {len(diff.changed)} changed, {len(diff.added)} added, "
                    f"{len(diff.removed)} removed in the graph"
                )
    if graph_changes:
        pruned = prune_orphan_texts(g)
        rebuild_search_index(g, db)
        print(
            f"[green]{graph_changes} ayas updated, {pruned} orphaned texts removed, "
            "search index rebuilt.[/green]"
        )
    else:
        print(f"[green]Graph already up to date.[/green] {files_written} bundled files rewritten.")
