from mim_ocr.optional_elements.easy_ocr import EasyOCRBackend
from mim_ocr.image import open_image

INPUT_DATA = {
    "example_image_path": "tests/input_data/example_report1.png",
}


def test_simple_easy_ocr(validate_cwd):
    img = open_image(INPUT_DATA["example_image_path"])
    assert EasyOCRBackend().run_ocr_to_box(img)
