
from typing import Optional

import numpy as np
import pandas as pd
from pytesseract import Output, pytesseract

from .backend import OCRBackend
from mim_ocr.data_model import Box
from mim_ocr.data_model.box import BoxType

DEFAULT_TESSERACT_CONFIG = r'--oem 1 --psm 3 -l pol'


class TesseractBackend(OCRBackend):
    def __init__(self, config: str = DEFAULT_TESSERACT_CONFIG):
        self.config = config

    def run_ocr_to_box(self, img: np.ndarray, *args, config: Optional[str] = None, **kwargs) -> Box:
        if config is None:
            config = self.config
        df = self.run_ocr_to_dataframe(img, config)
        return self.dataframe_to_box(df)

    def run_ocr_to_dataframe(self, img: np.ndarray, config: Optional[str]) -> pd.DataFrame:
        if config is None:
            config = self.config
        if img is None:
            raise ValueError("Input image cannot be None")
        d = pytesseract.image_to_data(img, output_type=Output.DICT, config=config)
        return pd.DataFrame.from_dict(d).astype({'conf': float})

    @staticmethod
    def dataframe_to_box(df: pd.DataFrame) -> Box:
        tree = Box.create_root_box()
        for _, row in df.iterrows():
            right = row.left + row.width
            bottom = row.top + row.height

            new_box = Box(left=row.left, top=row.top, right=right, bottom=bottom,
                          conf=row.conf, text=row.text, box_type=BoxType(row.level))
            tree.add_box_based_on_type(new_box)

        return tree

    @staticmethod
    def calc_average_line_len(box: Box) -> float:
        """Returns average line if found lines. Useful e.g. to assess image rotation."""

        text_lines_boxes = box.get_subboxes(box_type=BoxType.TESSERACT_LINE)
        return sum([text_line_box.width() for text_line_box in text_lines_boxes]) / len(text_lines_boxes)
