from typing import Tuple
from abc import ABC, abstractmethod
from enum import Enum

import numpy as np
from igraph import Vertex, Graph, Edge

from mim_ocr.data_model.box import Box
from mim_ocr.graph.graph_utils import boxes_horizontal_distance, boxes_verdical_distance


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
    class HorizontalDirection(Enum):
        LEFT = 0
        SAME = 1
        RIGHT = 2

    class VerdicalDirection(Enum):
        UP = 0
        SAME = 1
        DOWN = 2

    @classmethod
    def build(cls, graph: Graph, vertex1: Vertex):
        for vertex2 in graph.vs:
            if vertex1 == vertex2:
                continue
            edge_properties = cls._find_properties(vertex1, vertex2)
            if len(edge_properties["directions"]) == 0:
                continue
            # builder_properties = {cls.__name__: edge_properties}

            if graph.are_connected(vertex1, vertex2):
                edge = graph.es[graph.get_eid(vertex1, vertex2)]
                edge.update_attributes(**edge_properties)
            else:
                graph.add_edge(vertex1, vertex2, **edge_properties)

    @classmethod
    def is_down_edge(cls, e: Edge):
        return (
            "verdical" in e.attributes()["directions"]
            and cls.HorizontalDirection.DOWN.value
            is e.attributes()["directions"]["verdical"].value
        )

    @classmethod
    def is_up_edge(cls, e: Edge):
        return (
            "verdical" in e.attributes()["directions"]
            and cls.HorizontalDirection.UP.value
            is e.attributes()["directions"]["verdical"].value
        )

    @classmethod
    def is_left_edge(cls, e: Edge):
        return (
            "horizontal" in e.attributes()["directions"]
            and cls.HorizontalDirection.LEFT.value
            is e.attributes()["directions"]["horizontal"].value
        )

    @classmethod
    def is_right_edge(cls, e: Edge):
        return (
            "horizontal" in e.attributes()["directions"]
            and cls.HorizontalDirection.RIGHT.value
            is e.attributes()["directions"]["horizontal"].value
        )

    @classmethod
    @abstractmethod
    def _find_properties(cls, vertex1: Vertex, vertex2: Vertex):
        raise NotImplementedError


class VerdicalEdgeBuilder(EdgeBuilder):
    @classmethod
    def _find_properties(cls, vertex1: Vertex, vertex2: Vertex):
        box_v = cls.get_box_for_vertex(vertex1)
        box_u = cls.get_box_for_vertex(vertex2)

        result = {"directions": {}}
        # if boxes verdical distance is to big
        if boxes_horizontal_distance(box_u, box_v) > 5.0:
            return result

        elif boxes_verdical_distance(box_u, box_v) > 700.0:
            return result

        if box_u.bottom < box_v.top:
            result["directions"]["verdical"] = cls.VerdicalDirection.UP
        elif box_u.top > box_v.bottom:
            result["directions"]["verdical"] = cls.VerdicalDirection.DOWN
        return result


class HorizontalEdgeBuilder(EdgeBuilder):
    @classmethod
    def _find_properties(cls, vertex1: Vertex, vertex2: Vertex):
        box_v = cls.get_box_for_vertex(vertex1)
        box_u = cls.get_box_for_vertex(vertex2)

        result = {"directions": {}}
        if boxes_verdical_distance(box_u, box_v) > 5.0:
            return result

        elif boxes_horizontal_distance(box_u, box_v) > 700.0:
            return result

        if box_u.right < box_v.left:
            result["directions"]["horizontal"] = cls.HorizontalDirection.LEFT
        elif box_u.left > box_v.right:
            result["directions"]["horizontal"] = cls.HorizontalDirection.RIGHT
        return result


class RadiusEdgeBuilder(EdgeBuilder):
    @classmethod
    def _find_properties(cls, vertex1: Vertex, vertex2: Vertex) -> dict:
        box_v = cls.get_box_for_vertex(vertex1)
        box_u = cls.get_box_for_vertex(vertex2)
        min_distance = cls.min_boxes_distance(box_v, box_u)
        result = {"directions": {}}

        # TODO move it somewhere else
        if min_distance <= 200.0:
            if box_u.right < box_v.left:
                result["directions"]["horizontal"] = cls.HorizontalDirection.LEFT
            elif box_u.left > box_v.right:
                result["directions"]["horizontal"] = cls.HorizontalDirection.RIGHT
            else:
                result["directions"]["horizontal"] = cls.HorizontalDirection.SAME

            if box_u.bottom < box_v.top:
                result["directions"]["verdical"] = cls.VerdicalDirection.UP
            elif box_u.top > box_v.bottom:
                result["directions"]["verdical"] = cls.VerdicalDirection.DOWN
            else:
                result["directions"]["verdical"] = cls.VerdicalDirection.SAME

        return result

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
        v_corners = cls.get_box_corners(v_box)
        u_corners = cls.get_box_corners(u_box)

        min_distance = float("inf")
        for p_v in v_corners:
            for p_u in u_corners:
                min_distance = min(min_distance, cls.points_distance(p_v, p_u))

        return min_distance
