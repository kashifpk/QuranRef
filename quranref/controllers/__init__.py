from .. import graph_models
from ..graph_models.quran_graph import QuranGraph


class GraphMixin(object):
    "Contains common code for handling results that are stored in graph db"

    def __init__(self):
        self.gdb = graph_models.gdb
        self.qgraph = QuranGraph.get_graph_instance(self.gdb)
