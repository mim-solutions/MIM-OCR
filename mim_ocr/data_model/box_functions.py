from typing import Optional
import numpy as np

from mim_ocr.backends import OCRBackend
from mim_ocr.data_model import Box
from mim_ocr.data_model.box import BoxType


def run_ocr_on_box(backend: OCRBackend, img: np.ndarray,
                   box: Box, box_type: Optional[BoxType] = None,
                   *args, **kwargs) -> Box:
    """
        Run OCR algorithm on the whole box structure.

        For each of subboxes we run OCR algorithm.

        Args:
            backend (OCRBackend)
            img (np.ndarray): An original image.
            box (Box): Root box computed on img.
            box_type (Optional[BoxType]): Run OCR only on boxes with this type.
    """
    assert box.box_type == BoxType.ROOT_BOX

    # reverse order is necessary, because we modify the children
    for b in box.reverse_order_traversal():

        if (box_type is not None) and (b.box_type != box_type):
            continue

        if b.box_type == BoxType.ROOT_BOX:
            continue

        run_ocr_on_single_box(backend, img, b, *args, **kwargs)

    return box


# In OCR-37 move as a method of OCRBackend class.
def run_ocr_on_single_box(backend: OCRBackend, img: np.ndarray,
                          box: Box, *args, **kwargs) -> Box:
    """ Run OCR algorithm on single box.

        When the new structure is identified on the box, we replace
        the children of the box by the newly identified children and reset the old text.
    """
    new_b = backend.run_ocr_to_box(img[box.top:box.bottom, box.left:box.right, :], *args, **kwargs)

    # We have to update the identified coordinates
    for b_elem in new_b.preorder_traversal():
        b_elem.top = box.top + b_elem.top
        b_elem.bottom = box.top + b_elem.bottom
        b_elem.left = box.left + b_elem.left
        b_elem.right = box.left + b_elem.right

    if len(new_b.children) > 0:
        box.children = new_b.children
        box.text = ''
        info_dict = {"recomputed_ocr": backend.__class__.__name__}
        box.additional_data.update(info_dict)

    return box
