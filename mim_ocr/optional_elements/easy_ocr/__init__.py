from easyocr import Reader
import numpy as np

from mim_ocr.backends import OCRBackend
from mim_ocr.data_model import Box
from mim_ocr.data_model.box import BoxType


class EasyOCRBackend(OCRBackend):

    def __init__(self):
        super().__init__()
        self.reader = Reader(['pl'])

    def run_ocr_to_box(self, img: np.ndarray, *args, **kwargs) -> Box:
        """
        EasyOCR does not return levels, so the output structure is simple:
        a dummy box with children.
        """
        res_list = self.reader.readtext(img, *args, **kwargs)

        tree = Box.create_root_box()
        for res in res_list:

            left, top = tuple(res[0][0])
            right, bottom = tuple(res[0][2])

            new_box = Box(left=int(left), top=int(top), right=int(right), bottom=int(bottom),
                          conf=100*res[2], text=res[1], box_type=BoxType.EASYOCR_BOX)
            Box.add_child(tree, new_box)

        return tree
