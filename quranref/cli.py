import typer

from .app_init import app_init
from .commands import db as cmd_db
from .commands import post_process as cmd_post_process

app = typer.Typer(name="QuranRef CLI")
app.add_typer(cmd_db.app, name="db", help="Manage database structure")
app.add_typer(
    cmd_post_process.app, name="post-process", help="Data post processing after import(s)"
)


def cli_init(ctx: typer.Context):
    app_init()


def main():
    app()
