from typing import Literal

from igraph import Vertex

from mim_ocr.data_model.box import Box
from mim_ocr.graph.builders import EdgeBuilder

Direction = Literal["left", "right", "up", "down"]


def boxes_verdical_distance(b1: Box, b2: Box) -> float:
    up = min(b1.top, b2.top)
    down = max(b1.bottom, b2.bottom)

    return down - up - b1.height() - b2.height()


def boxes_horizontal_distance(b1: Box, b2: Box) -> float:
    left = min(b1.left, b2.left)
    right = max(b1.right, b2.right)

    return right - left - b1.width() - b2.width()


def get_neighbours(vertex: Vertex, direction: Direction, sorted: bool = True):
    direction_function = None
    match direction:
        case "left":
            direction_function = EdgeBuilder.is_left_edge
        case "right":
            direction_function = EdgeBuilder.is_right_edge
        case "up":
            direction_function = EdgeBuilder.is_up_edge
        case "down":
            direction_function = EdgeBuilder.is_down_edge
        case _:
            direction_function = None

    assert direction_function is not None, "direction argument is invalid"

    edges = vertex.out_edges()
    filtered_neighbours = [
        edge.target_vertex for edge in edges if EdgeBuilder.is_right_edge(edge)
    ]
    if sorted:
        match direction:
            case "left":
                filtered_neighbours.sort(key=lambda x: x["box"].left, reverse=True)
            case "right":
                filtered_neighbours.sort(key=lambda x: x["box"].right)
            case "up":
                filtered_neighbours.sort(key=lambda x: x["box"].top, reverse=True)
            case "down":
                filtered_neighbours.sort(key=lambda x: x["box"].bottom)
    return filtered_neighbours
