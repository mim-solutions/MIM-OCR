import math
from typing import Union, Tuple

import cv2
import numpy as np
from deskew import determine_skew
from scipy.ndimage import interpolation


def deskew_cv2(image: np.ndarray,
               method: str = "projection_profile",
               projection_delta: float = 0.5,
               projection_limit: int = 10,
               background: Union[int, Tuple[int, int, int]] = (0, 0, 0)) -> Tuple[np.ndarray, float]:
    if method == "hough_transform":
        best_angle = _determine_best_angle_hough_transform(image)
    elif method == "projection_profile":
        best_angle = _determine_best_angle_projection_profile(image, projection_delta, projection_limit)
    else:
        raise ValueError(f"Unknown deskew method: {method}")
    if best_angle == 0.0:
        return image, best_angle
    return rotate_cv2(image, best_angle, background), best_angle


def _determine_best_angle_hough_transform(image: np.ndarray) -> float:
    """See more: https://github.com/sbrunner/deskew"""
    if len(image.shape) == 3:
        img_grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        img_grayscale = image

    blur = cv2.medianBlur(img_grayscale, 3)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    angle = determine_skew(thresh, num_angles=360, sigma=2.0,
                           num_peaks=40)  # small variation of default parameters obtained by trial and error
    if angle is None:
        return 0.0
    return float(angle)


def _determine_best_angle_projection_profile(image: np.ndarray, delta: float = .5, limit: int = 10) -> float:
    """Here's a modified implementation of the Projection Profile Method to correct skewed images
    as described in Projection profile based skew estimation algorithm for JBIG compressed images.
    After obtaining a binary image, the idea is to rotate the image at various angles and generate
    a histogram of pixels in each iteration. To determine the skew angle, we compare the maximum difference
    between peaks and using this skew angle, rotate the image to correct the skew. The amount of peaks
    to determine can be adjusted by the delta value, the lower the delta, the more peaks will be checked
    with the tradeoff that the process will take longer.
      - https://stackoverflow.com/questions/59660933/how-to-de-skew-a-text-image-also-retrieve-the-new-bounding-box-of-that-image  # noqa
      - http://www.cvc.uab.es/~bagdanov/pubs/ijdar98.pdf
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 3)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    scores = []
    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        histogram, score = _determine_projection_profile_score(thresh, angle)
        scores.append(score)

    return angles[scores.index(max(scores))]


def _determine_projection_profile_score(arr, angle):
    data = interpolation.rotate(arr, angle, reshape=False, order=0)
    histogram = np.sum(data, axis=1)
    score = np.sum((histogram[1:] - histogram[:-1]) ** 2)
    return histogram, score


def get_rotation_matrix_cv2(image: np.ndarray, angle: float) -> Tuple[np.ndarray, float, float]:
    """Returs rotation_matrix and dimensions of result image (height, width)
    Source: deskew Readme (https://github.com/sbrunner/deskew)"""
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2

    return rot_mat, height, width


def rotate_cv2(
        image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]
) -> np.ndarray:
    """Source: deskew Readme (https://github.com/sbrunner/deskew)"""

    # TODO: Check Another rotation method with different size, interpolation and border mode
    # (h, w) = image.shape[:2]
    # center = (w // 2, h // 2)
    # m = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    # rotated = cv2.warpAffine(image, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE, )
    rot_mat, height, width = get_rotation_matrix_cv2(image, angle)

    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)
