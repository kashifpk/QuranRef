import typer

from .graph_models import get_gdb
from .graph_models.quran_graph import QuranGraph

cmd_app = typer.Typer()


@cmd_app.command()
def populate():
    """Create database tables and graph."""
    print("Creating tables and graph")
    gdb = get_gdb()
    db_objects = [QuranGraph]
    gdb.create_all(db_objects)


@cmd_app.command()
def test():
    """A test command."""
    print("Hi, just testing")


def main():
    cmd_app()
