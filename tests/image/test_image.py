from pathlib import Path
import numpy as np

from mim_ocr.image import open_image, open_pdf

INPUT_DATA = {
    "all_image_formats_dir": Path("tests/input_data/all_image_formats"),
    "pdfs_dir": Path("tests/input_data/pdfs"),
}


def test_simple_open_pdf(validate_cwd):
    for path in INPUT_DATA['pdfs_dir'].iterdir():
        for img in open_pdf(path):
            assert isinstance(img, np.ndarray)


def test_simple_open_image(validate_cwd):
    for path in INPUT_DATA['all_image_formats_dir'].iterdir():
        assert isinstance(open_image(path), np.ndarray)
