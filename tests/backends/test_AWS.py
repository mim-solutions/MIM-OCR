from mim_ocr.backends.aws_textract import AwsTextractBackend
from mim_ocr.image import open_image

INPUT_DATA = {
    "example_image_path": "tests/input_data/example_report1.png",
}


def test_simple_aws_textract_ocr(validate_cwd):
    img = open_image(INPUT_DATA["example_image_path"])
    box = AwsTextractBackend().run_ocr_to_box(img)
    assert box.calc_confidence()['total_letters'] > 900
