from typing import Tuple
from abc import ABC, abstractmethod
from enum import Enum
from typing import Literal

import numpy as np
from igraph import Vertex, Graph, Edge

from mim_ocr.data_model.box import Box
from mim_ocr.graph.graph_utils import boxes_horizontal_distance, boxes_vertical_distance

Direction = Literal["left", "right", "up", "down"]


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

    class VerticalDirection(Enum):
        UP = 0
        SAME = 1
        DOWN = 2

    @classmethod
    def build(cls, graph: Graph, vertex: Vertex):
        vertex1 = vertex
        for vertex2 in graph.vs:
            if vertex1 == vertex2:
                continue
            edge_properties = cls._find_properties(vertex1, vertex2)
            if len(edge_properties["directions"]) == 0:
                continue

            if graph.are_connected(vertex1, vertex2):
                edge = graph.es[graph.get_eid(vertex1, vertex2)]
                edge.update_attributes(**edge_properties)
            else:
                graph.add_edge(vertex1, vertex2, **edge_properties)

    @classmethod
    def is_down_edge(cls, e: Edge):
        return (
            "vertical" in e.attributes()["directions"]
            and cls.VerticalDirection.DOWN.value
            is e.attributes()["directions"]["vertical"].value
        )

    @classmethod
    def is_up_edge(cls, e: Edge):
        return (
            "vertical" in e.attributes()["directions"]
            and cls.VerticalDirection.UP.value
            is e.attributes()["directions"]["vertical"].value
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
    def get_neighbours(cls, vertex: Vertex, direction: Direction, sorted: bool = True):
        direction_function = None

        if direction == "left":
            direction_function = cls.is_left_edge
        elif direction == "right":
            direction_function = cls.is_right_edge
        elif direction == "up":
            direction_function = cls.is_up_edge
        elif direction == "down":
            direction_function = cls.is_down_edge

        assert direction_function is not None, "direction argument is invalid"

        edges = vertex.out_edges()
        filtered_neighbours = [
            edge.target_vertex for edge in edges if direction_function(edge)
        ]
        if sorted:
            if direction == "left":
                filtered_neighbours.sort(key=lambda x: x["box"].right, reverse=True)
            elif direction == "right":
                filtered_neighbours.sort(key=lambda x: x["box"].left)
            elif direction == "up":
                filtered_neighbours.sort(key=lambda x: x["box"].bottom, reverse=True)
            elif direction == "down":
                filtered_neighbours.sort(key=lambda x: x["box"].top)
        return filtered_neighbours

    @classmethod
    @abstractmethod
    def _find_properties(cls, vertex1: Vertex, vertex2: Vertex):
        raise NotImplementedError


class VerticalEdgeBuilder(EdgeBuilder):
    # Acceptable distantances to create an edge
    horizontal_acceptable_distance = 5.0
    vertical_acceptable_distance = 700.0

    @classmethod
    def _find_properties(cls, vertex1: Vertex, vertex2: Vertex) -> dict:
        box1 = cls.get_box_for_vertex(vertex1)
        box2 = cls.get_box_for_vertex(vertex2)

        result = {"directions": {}}
        # if boxes vertical distance is to big
        if boxes_horizontal_distance(box2, box1) > cls.horizontal_acceptable_distance:
            return result

        elif boxes_vertical_distance(box2, box1) > cls.vertical_acceptable_distance:
            return result

        if box2.bottom < box1.top:
            result["directions"]["vertical"] = cls.VerticalDirection.UP
        elif box2.top > box1.bottom:
            result["directions"]["vertical"] = cls.VerticalDirection.DOWN

        return result


class HorizontalEdgeBuilder(EdgeBuilder):
    # Acceptable distantances to create an edge
    horizontal_acceptable_distance = 700.0
    vertical_acceptable_distance = 5.0

    @classmethod
    def _find_properties(cls, vertex1: Vertex, vertex2: Vertex):
        box1 = cls.get_box_for_vertex(vertex1)
        box2 = cls.get_box_for_vertex(vertex2)

        result = {"directions": {}}
        if boxes_vertical_distance(box2, box1) > cls.vertical_acceptable_distance:
            return result

        elif boxes_horizontal_distance(box2, box1) > cls.horizontal_acceptable_distance:
            return result

        if box2.right < box1.left:
            result["directions"]["horizontal"] = cls.HorizontalDirection.LEFT
        elif box2.left > box1.right:
            result["directions"]["horizontal"] = cls.HorizontalDirection.RIGHT
        return result


class RadiusEdgeBuilder(EdgeBuilder):
    # maximum acceptable distance to create an edge
    maximum_radius = 200.0

    @classmethod
    def _find_properties(cls, vertex1: Vertex, vertex2: Vertex) -> dict:
        box1 = cls.get_box_for_vertex(vertex1)
        box2 = cls.get_box_for_vertex(vertex2)
        min_distance = cls.min_boxes_distance(box1, box2)
        result = {"directions": {}}

        if min_distance <= cls.maximum_radius:
            if box2.right < box1.left:
                result["directions"]["horizontal"] = cls.HorizontalDirection.LEFT
            elif box2.left > box1.right:
                result["directions"]["horizontal"] = cls.HorizontalDirection.RIGHT
            else:
                result["directions"]["horizontal"] = cls.HorizontalDirection.SAME

            if box2.bottom < box1.top:
                result["directions"]["vertical"] = cls.VerticalDirection.UP
            elif box2.top > box1.bottom:
                result["directions"]["vertical"] = cls.VerticalDirection.DOWN
            else:
                result["directions"]["vertical"] = cls.VerticalDirection.SAME

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
