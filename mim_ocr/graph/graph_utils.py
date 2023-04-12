from typing import Optional
from mim_ocr.data_model.box import Box
from igraph import Graph, Vertex


def get_vertex_with_text(text: str, graph: Graph) -> Optional[Vertex]:
    for v in graph.vs:
        if text in v["box"].text:
            return v
    return None


# distance in the following function may be negative if boxes overlap verically
def boxes_vertical_distance(b1: Box, b2: Box) -> float:
    up = min(b1.top, b2.top)
    down = max(b1.bottom, b2.bottom)

    return down - up - b1.height() - b2.height()


# distance in the following function may be negative if boxes overlap horizontally
def boxes_horizontal_distance(b1: Box, b2: Box) -> float:
    left = min(b1.left, b2.left)
    right = max(b1.right, b2.right)

    return right - left - b1.width() - b2.width()
