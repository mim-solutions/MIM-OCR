from igraph import Vertex
import numpy as np
from PIL import Image, ImageDraw

from mim_ocr.data_model.box import Box
from mim_ocr.graph.builders import EdgeBuilder


def get_box_center(box: Box) -> tuple:
    return (box.left + box.width() / 2), (box.top + box.height() / 2)


def draw_neighbourhood(v: Vertex, img: np.array) -> np.ndarray:
    pil_image = Image.fromarray(img)
    draw_image = ImageDraw.Draw(pil_image)
    draw_image.rectangle(
        [v["box"].left, v["box"].top, v["box"].right, v["box"].bottom],
        outline="red",
        width=3,
    )

    v_center = get_box_center(v["box"])

    for mode in ["left", "right", "up", "down"]:
        verticies = EdgeBuilder.get_neighbours(v, mode)
        for u in verticies:
            u_center = get_box_center(u["box"])
            draw_image.rectangle(
                [u["box"].left, u["box"].top, u["box"].right, u["box"].bottom],
                outline="green",
                width=3,
            )
            draw_image.line([v_center, u_center], fill="blue", width=1)

    return np.array(pil_image)
