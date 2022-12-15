from mim_ocr.backends.google_vision import GCPBackend
from mim_ocr.image import open_image

INPUT_DATA = {
    "example_tesseract_image_path": "tests/input_data/example_report1.png",
}


def test_gcp_to_box(validate_cwd):
    img = open_image(INPUT_DATA["example_tesseract_image_path"])
    box = GCPBackend().run_ocr_to_box(img)
    assert box.calc_confidence()['total_letters'] > 900
