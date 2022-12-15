import pandas as pd

from mim_ocr.backends.tesseract import TesseractBackend
from mim_ocr.data_model.box import BoxType
from mim_ocr.image import open_image

INPUT_DATA = {
    "example_image_path": "tests/input_data/example_report1.png",
    "example_tesseract_dataframe1_path": "tests/input_data/example_tesseract_dataframe.xlsx",
}


def test_simple_tesseract_ocr(validate_cwd):
    img = open_image(INPUT_DATA["example_image_path"])
    assert TesseractBackend().run_ocr_to_box(img)


def test_from_tesseract_dataframe(validate_cwd):
    dataframe_path = INPUT_DATA["example_tesseract_dataframe1_path"]
    backend = TesseractBackend()
    box = backend.dataframe_to_box(pd.read_excel(dataframe_path))
    expected = 267.5
    actual = backend.calc_average_line_len(box)
    assert actual == expected
    assert box.parent is None
    assert len(box.children) == 1
    lv1_box = box.children[0]
    assert lv1_box.box_type == BoxType.TESSERACT_DOCUMENT
    assert len(lv1_box.children) == 2
    lv2_box_0 = lv1_box.children[0]
    assert lv2_box_0.box_type == BoxType.TESSERACT_PAGE
    lv2_1_lv4_box = lv1_box.children[1].children[0].children[0]
    assert [b.text for b in lv2_1_lv4_box.children] == [
        "Ab", "anti", "FOSFOLIPIDI:"]
