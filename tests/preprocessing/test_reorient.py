import pytest
from mim_ocr.preprocessing import reorient
import cv2


@pytest.mark.parametrize("angle", [0, 90, 180, 270])
def test_reorient(angle, validate_cwd):

    input_image_path_format = "tests/input_data/example_report1-reorient{}.png"
    input_image_path = input_image_path_format.format(str(angle))
    input_image = cv2.imread(input_image_path)

    _, determined_reorient_angle = reorient.reorient_cv2(input_image, input_image_path)

    # angle, which is needed to reorient image to normal
    expected_reorient_angle = (360 - angle) % 360

    assert determined_reorient_angle == expected_reorient_angle
