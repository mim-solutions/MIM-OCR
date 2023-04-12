from mim_ocr.backends.tesseract import TesseractBackend
from mim_ocr.image import open_image
from mim_ocr.data_model.box import BoxType
from mim_ocr.graph.graph_utils import get_vertex_with_text
from mim_ocr.graph.graph_model import GraphFactory
from mim_ocr.graph.builders import (
    VerticalEdgeBuilder,
    HorizontalEdgeBuilder,
    EdgeBuilder,
)

INPUT_DATA = {
    "example_path": "tests/input_data/example_report1.png",
}


def test_graph_simple():
    img = open_image(INPUT_DATA["example_path"])
    box = TesseractBackend().run_ocr_to_box(img)
    gf = GraphFactory(edge_builders=[VerticalEdgeBuilder, HorizontalEdgeBuilder])
    graph = gf.build_graph_for_root_box(box, BoxType.TESSERACT_WORD)

    v = get_vertex_with_text(text="PESEL", graph=graph)
    right = EdgeBuilder.get_neighbours(v, "right")
    left = EdgeBuilder.get_neighbours(v, "left")
    up = EdgeBuilder.get_neighbours(v, "up")
    down = EdgeBuilder.get_neighbours(v, "down")

    r_values = [v["box"].left for v in right]
    l_values = [v["box"].right for v in left]
    d_values = [v["box"].top for v in down]
    u_values = [v["box"].bottom for v in up]

    assert all(x <= y for x, y in zip(r_values, r_values[1:]))
    assert all(x >= y for x, y in zip(l_values, l_values[1:]))
    assert all(x <= y for x, y in zip(d_values, d_values[1:]))
    assert all(x >= y for x, y in zip(u_values, u_values[1:]))
    assert down[0]["box"].text == "89012201133"
