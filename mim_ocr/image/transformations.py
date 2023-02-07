from pathlib import Path
from typing import Dict

import numpy as np

from mim_ocr.preprocessing import deskew_cv2, reorient_cv2


def no_transform(img: np.ndarray, path: Path, metadata: Dict) -> np.ndarray:
    return img


def reorient(img: np.ndarray, path: Path, metadata: Dict) -> np.ndarray:
    img, orientation = reorient_cv2(img, image_path=path)
    metadata['orientation'] = orientation
    return img


def deskew(img: np.ndarray, path: Path, metadata: Dict) -> np.ndarray:
    img, angle = deskew_cv2(img)
    metadata['angle'] = f"{angle:.2}"
    return img
