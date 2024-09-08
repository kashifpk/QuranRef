import typer

from .app_init import app_init
from .commands import db as cmd_db

app = typer.Typer(name="QuranRef CLI")
app.add_typer(cmd_db.app, name="db", help="Manage database structure")


def cli_init(ctx: typer.Context):
    app_init()


def main():
    app()
