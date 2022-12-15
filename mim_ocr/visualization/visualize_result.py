from typing import Optional, Any, Dict, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from mim_ocr.data_model.box import Box, BoxType
from mim_ocr.utils import isnan

"""
Script visualizes tesseract results on all files in a directory.
Displays:
 - original image with tesseract boxes
 - image with parsed text and tesseract boxes

usage: tesseract_tests dirname
"""

COLORS = [
    (200, 200, 0),
    (255, 0, 0),
    (0, 255, 0),
    (0, 204, 205),
    (170, 0, 255),
    (255, 127, 0),
    (0, 149, 255),
    (255, 0, 170),
]
COLOR_WHITE = (255, 255, 255)

FONT_COLOR = (0, 0, 0)
FONT_PATH = "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
ADDITIONAL_INFO_FONT_SIZE = 12


def visualize_ocr_result(original_image: np.ndarray,
                         box: Box,
                         metadata: Optional[Dict[str, Any]] = None,
                         confidence_threshold: float = 0.0,
                         show_confidence: bool = True,
                         additional_value_to_show: Optional[str] = None,
                         show_only_text_with_additional_value: bool = False,
                         show_outer_boxes: bool = True,
                         only_type: Optional[BoxType] = None,
                         only_original: bool = False,
                         only_ocr_result: bool = False,
                         ) -> np.ndarray:
    """Creates image that visualizes OCR results:
    On left half of the image are shown:
      - original image
      - boxes showing places of OCR
    On right half are shown:
      - boxes showing places of OCR
      - text with OCR result
      - OCR confidence for each text (or additional value if specified)
      - additional information in form of metadata

    Args:
        original_image (np.ndarray): original image (shown as reference).
        box (Box): Box object with OCR results.
        metadata (Optional[Dict[str, Any]]): additional dictionary with additional image legend.
        confidence_threshold (float): between 0.0 to 100.0
        show_confidence (bool): should additional info about word confidence be presented
        additional_value_to_show (Optional[str]): name of key in box items additional data dictionary
                                                  that would be presented instead of confidence.
                                                  This cannot be used together with show_confidence=True.
        show_only_text_with_additional_value (bool): Should shown word be limited to only those
                                                     that have an additional value.
        show_outer_boxes (bool): If should be plotted also bigger boxes (level below the word), default True.
        only_type (Optional[BoxType]): If not None, show only boxes with the specified type, default None.
        only_original: If only original image with bounding boxes should be visualize, defult False
        only_ocr_result: If only OCR parsed image with bounding boxes should be visualize, defult False

    Returns:
        visualization image as ndarray (cv2 image)
    """

    if show_confidence and additional_value_to_show:
        raise ValueError("Cannot show confidence and additional_value.")

    h, w, c = original_image.shape

    # enlarge image to have place to visualize parsed_image
    new_img = np.zeros((h, 2 * w, c), np.uint8)
    new_img[:, :] = COLOR_WHITE
    new_img[0:h, 0:w] = original_image.copy()

    box_type_color_mapping = _generate_box_type_color_mapping(box)

    if show_outer_boxes:
        new_img = add_outer_boxes(
            new_img, box, box_type_color_mapping, confidence_threshold, w,
            only_type=only_type, only_original=only_original)

    if only_original:
        return new_img[:, :w, :]

    # add text on parsed image
    im_parsed = Image.fromarray(new_img)
    draw = ImageDraw.Draw(im_parsed)

    for b in box.preorder_traversal():

        if (b.conf is not None) and (b.conf < confidence_threshold):

            if not show_outer_boxes:
                continue
            if b.conf != -1:
                continue

        if isnan(b.text):
            continue

        if additional_value_to_show:
            if show_only_text_with_additional_value \
                and (additional_value_to_show not in b.additional_data
                     or isnan(b.additional_data[additional_value_to_show])
                     or not b.additional_data[additional_value_to_show]):
                continue

        (x2, y2, w2, h2) = (b.left, b.top, b.width(), b.height())

        fontsize, _ = get_optimal_pillow_font_size(w=w2, h=h2, txt=b.text, d=draw)
        font = ImageFont.truetype(FONT_PATH, fontsize)

        draw.text(xy=(x2 + w, y2), text=b.text, fill=(0, 0, 0), font=font, spacing=0)

        if show_confidence and b.text:
            additional_info_font = ImageFont.truetype(FONT_PATH, ADDITIONAL_INFO_FONT_SIZE)
            draw.text(xy=(x2 + w, y2 - 12), text=f"{b.conf:.1f}", fill=(0, 200, 0), font=additional_info_font,
                      spacing=0)  # parameters obtained by trial and error

        if additional_value_to_show and \
                (additional_value_to_show in b.additional_data) \
                and not isnan(b.additional_data[additional_value_to_show]):
            additional_info_font = ImageFont.truetype(FONT_PATH, ADDITIONAL_INFO_FONT_SIZE)
            draw.text(xy=(x2 + w, y2 - 12), text=f"{b.additional_data[additional_value_to_show]}", fill=(0, 200, 0),
                      font=additional_info_font,
                      spacing=0)  # parameters obtained by trial and error

    # show metadata
    if metadata is not None:
        metadata_fontsize = 40

        metadata_str = "".join(f'{k}: {v}\n' for k, v in metadata.items())

        metadata_font = ImageFont.truetype(FONT_PATH, metadata_fontsize)
        draw.text(xy=(w, 0), text=metadata_str, fill=(0, 200, 0), font=metadata_font, spacing=4)

    if only_ocr_result:
        return np.array(im_parsed)[:, w:, :]

    return np.array(im_parsed)


def add_outer_boxes(
        image: np.ndarray,
        box: Box,
        box_type_color_mapping: Dict[BoxType, Tuple[int, int, int]],
        confidence_threshold: float,
        width: int,
        only_type: Optional[BoxType] = None,
        only_original: bool = False,
) -> np.ndarray:
    for b in box.preorder_traversal():
        if (b.conf is not None) and (b.conf < confidence_threshold):
            if b.conf != -1:
                continue

        if (only_type is not None) and (b.box_type != only_type):
            continue

        # add boxes on the original
        color = box_type_color_mapping[b.box_type]

        image = cv2.rectangle(image, (b.left, b.top), (b.right, b.bottom), color, thickness=2)
        # add boxes on parsed image
        if not only_original:
            image = cv2.rectangle(image, (b.left + width, b.top), (b.right + width, b.bottom), color, thickness=2)

    return image


def get_optimal_pillow_font_size(w: int, h: int, txt: str, d: ImageDraw.Draw) -> Tuple[int, int]:
    """Calculates which font size to use to fill box.
    Uses binary search by font size (with max 20 trials)."""
    font_size = 1
    font_min = 0
    font_max = 0
    for i in range(20):
        new_font = ImageFont.truetype(FONT_PATH, font_size)
        txt_width, txt_height = d.textsize(txt, font=new_font)
        if txt_width == w and txt_height == h:
            return font_size, txt_height
        elif txt_width > w or txt_height > h:
            font_max = font_size
            next_font_size = (font_min + font_size) // 2
        else:
            font_min = font_size
            if font_max:
                next_font_size = (font_max + font_size) // 2
            else:
                next_font_size = font_size * 2

        if next_font_size == font_size:
            return font_size, txt_height
        font_size = next_font_size
    return font_size, txt_height


def compare_ocr_results(img: np.ndarray, box1: Box, box2: Box,
                        confidence_threshold1: float = 0.0,
                        confidence_threshold2: float = 0.0) -> np.ndarray:
    """Creates image that visualizes OCR results:
    On top of the image is shown original image.
    Below on the left half of the image are shown results from the first OCR method:
      - boxes showing places of OCR
      - text with OCR result
    On the right half are shown results from the second OCR method:
      - boxes showing places of OCR
      - text with OCR result

    Args:
        img (np.ndarray): original image (shown as reference).
        box1 (Box): Box object with OCR results.
        box2 (Box): Box object with OCR results.

    Returns:
        visualization image as ndarray (cv2 image)
    """

    h, w, c = img.shape

    # enlarge image to have place to visualize parsed_image
    new_img = np.zeros((2 * h, 2 * w, c), np.uint8)
    new_img[:, :] = COLOR_WHITE
    new_img[0:h, 0:w] = img.copy()

    for box, shift, thres in [(box1, 0, confidence_threshold1), (box2, w, confidence_threshold2)]:
        for b in box.preorder_traversal():

            if (b.conf is not None) and (b.conf < thres):
                continue

            level = b.box_type.value
            col = COLORS[level - 1]

            # add boxes on parsed image
            new_img = cv2.rectangle(new_img, (b.left + shift, b.top + h), (b.right + shift, b.bottom + h), col, 2)

    # add text on parsed image
    im_parsed = Image.fromarray(new_img)
    draw = ImageDraw.Draw(im_parsed)

    for box, shift, thres in [(box1, 0, confidence_threshold1), (box2, w, confidence_threshold2)]:

        for b in box.preorder_traversal():
            if (b.conf is not None) and (b.conf < thres):
                continue
            if isnan(b.text):
                continue

            (x2, y2, w2, h2) = (b.left, b.top, b.width(), b.height())

            fontsize, _ = get_optimal_pillow_font_size(w=w2, h=h2, txt=b.text, d=draw)
            font = ImageFont.truetype(FONT_PATH, fontsize)

            draw.text(xy=(x2 + shift, y2 + h), text=b.text, fill=(0, 0, 0), font=font, spacing=0)

    return np.array(im_parsed)


def _generate_box_type_color_mapping(box: Box) -> Dict[BoxType, Tuple[int, int, int]]:
    used_colors = 0
    mapping: Dict[BoxType, Tuple[int, int, int]] = {}
    for b in box.preorder_traversal():
        if b.box_type not in mapping:
            mapping[b.box_type] = COLORS[used_colors]
            used_colors += 1
    return mapping
