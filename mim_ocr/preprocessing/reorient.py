from pathlib import Path
from typing import Tuple

import cv2
import numpy as np
from pytesseract import pytesseract, Output

MINIMAL_REORIENTATION_CONFIDENCE = 3.0


def reorient_cv2(image: np.ndarray, image_path: Path) -> Tuple[np.ndarray, int]:
    # We need to add path due to strange tesseract errors.
    # https://stackoverflow.com/questions/67018785/why-pytesseract-cant-handle-osd-mode
    # if image_path is None:
    #     im = Image.fromarray(image)
    #     temp = tempfile.NamedTemporaryFile()
    #     temp.write(im.tobytes())
    #     image_path = temp.name
    # else:
    #     image_path = str(image_path)

    osd = pytesseract.image_to_osd(str(image_path), output_type=Output.DICT)
    rotation = osd['rotate']
    confidence = osd['orientation_conf']
    if confidence < MINIMAL_REORIENTATION_CONFIDENCE:
        rotation = 0

    return _reorient_image(image, rotation), rotation


def _reorient_image(image: np.ndarray, angle: int):
    if angle == 0:
        return image
    elif angle == 90:
        return cv2.rotate(image, cv2.cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(image, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
    raise ValueError("Incorrect rotation. Must be multiple of 90.")
