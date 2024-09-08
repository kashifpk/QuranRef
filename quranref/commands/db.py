import typer
from rich import print

from ..db import db as get_db
from ..models import QuranGraph


app = typer.Typer(name="Database structure related operations")

@app.command()
def init():
    db = get_db()
    db.create_all([QuranGraph])

    print("[green]Database initialization done.[/green]")
