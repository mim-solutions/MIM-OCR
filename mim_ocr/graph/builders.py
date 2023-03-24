from typing import Tuple
from abc import ABC, abstractmethod
from enum import Enum

from igraph import Vertex, Graph


class Builder(ABC):
    @classmethod
    def get_box_for_vertex(cls, vertex: Vertex) -> Box:
        return vertex["box"]


class VertexBuilder(Builder):
    @classmethod
    @abstractmethod
    def build(cls, graph: Graph, vertex: Vertex):
        raise NotImplementedError


class EdgeBuilder(Builder):
    class EdgeDirection(Enum):
        up = 0
        left = 1
        down = 2
        right = 3

    @classmethod
    def build(cls, graph: Graph, vertex1: Vertex, vertex2: Vertex):
        edge_properties = cls._find_properties(vertex1, vertex2)
        builder_properties = {EdgeBuilder.__name__: edge_properties}
        if graph.are_connected(vertex1, vertex2):
            ## TODO test that one
            edge = graph.eid(vertex1, vertex2)
            edge.update_attributes(builder_properties)
        else:
            graph.add_edge(vertex1, vertex2, **builder_properties)

    @classmethod
    @abstractmethod
    def _find_properties(cls, vertex1: Vertex, vertex2: Vertex):
        raise NotImplementedError


class SimpleEdgeBuilder(EdgeBuilder):
    @classmethod
    def _find_properties(cls, vertex1: Vertex, vertex2: Vertex) -> dict:
        box_v = SimpleEdgeBuilder.get_box_for_vertex(vertex1)
        box_u = SimpleEdgeBuilder.get_box_for_vertex(vertex2)
        min_distance = SimpleEdgeBuilder.min_boxes_distance(box_v, box_u)
        directions = []

        SimpleEdgeBuilder.EdgeDirection.down
        if min_distance <= 5.0:
            if box_u.right < box_v.left:
                directions.append(SimpleEdgeBuilder.EdgeDirection.left)
            elif box_u.left > box_v.right:
                directions.append(SimpleEdgeBuilder.EdgeDirection.right)
            if box_u.bottom < box_v.top:
                directions.append(SimpleEdgeBuilder.EdgeDirection.top)
            elif box_u.top > box_v.bottom:
                directions.append(SimpleEdgeBuilder.EdgeDirection.bottom)

        return {"directions": directions}

    @classmethod
    def get_box_corners(cls, box: Box) -> list[tuple[int, int]]:
        return [
            (box.left, box.top),
            (box.left, box.bottom),
            (box.right, box.top),
            (box.right, box.bottom),
        ]

    @classmethod
    def points_distance(cls, p1: Tuple[float, float], p2: Tuple[float, float]):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] + p2[1]) ** 2)

    @classmethod
    def min_boxes_distance(cls, v_box: Box, u_box: Box) -> Tuple[float]:
        v_corners = SimpleEdgeBuilder.get_box_corners(v_box)
        u_corners = SimpleEdgeBuilder.get_box_corners(u_box)

        min_distance = float("inf")
        for p_v in v_corners:
            for p_u in u_corners:
                min_distance = min(
                    min_distance, SimpleEdgeBuilder.points_distance(p_v, p_u)
                )

        return min_distance
