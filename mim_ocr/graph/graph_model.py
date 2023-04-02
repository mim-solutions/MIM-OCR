from typing import Optional

from igraph import Graph

from mim_ocr.data_model.box import Box, BoxType
from mim_ocr.graph.builders import VertexBuilder, EdgeBuilder


class GraphFactory:
    def __init__(
        self,
        vertex_builders: Optional[list[VertexBuilder]] = None,
        edge_builders: Optional[list[EdgeBuilder]] = None,
    ):
        self.vertex_builders = [] if vertex_builders is None else vertex_builders
        self.edge_builders = [] if edge_builders is None else edge_builders

    def build_graph_for_root_box(self, root_box: Box, layer: BoxType):
        boxes = root_box.get_subboxes(box_type=layer)
        return self.build_graph(boxes)

    def build_graph(self, boxes: list[Box]) -> Graph:
        graph = Graph(directed=True)

        for box in boxes:
            vertex = graph.add_vertex()
            vertex["box"] = box

        for vertex in graph.vs:
            for builder in self.vertex_builders:
                builder.build(graph, vertex)

        for builder in self.edge_builders:
            for vertex in graph.vs:
                builder.build(graph, vertex)
        return graph
