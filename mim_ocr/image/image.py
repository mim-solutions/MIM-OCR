from pathlib import Path
from typing import List

import cv2
import numpy as np
import pdf2image
from PIL import Image


def open_image(path: Path) -> np.ndarray:
    """ Opens image from path as cv2 matrix.
        Using PIL.Image as a proxy here gives us support for all image formats supported by tesseract:
        https://github.com/tesseract-ocr/tessdoc/blob/main/InputFormats.md
    """
    with Image.open(path) as pil_image:
        return pil_image_to_cv2(pil_image)


def pil_image_to_cv2(pil_image: Image) -> np.ndarray:
    # based on https://stackoverflow.com/questions/14134892/convert-image-from-pil-to-opencv-format
    return cv2.cvtColor(np.array(pil_image.convert('RGB')), cv2.COLOR_RGB2BGR)


def open_pdf(path: Path) -> List[np.ndarray]:
    return [pil_image_to_cv2(pil_image)
            for pil_image in pdf2image.convert_from_path(path)]


def write_image(img: np.ndarray, path: Path):
    """ based on: https://stackoverflow.com/a/11335576/3178243
    """
    cv2.imwrite(str(path), img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
