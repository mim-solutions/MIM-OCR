from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from mim_ocr.data_model import Box
from mim_ocr.utils.class_utils import get_subclass_by_name


class OCRBackend(ABC):

    @abstractmethod
    def run_ocr_to_box(self, img: np.ndarray, *args, **kwargs) -> Box:
        pass

    def run_ocr_to_dataframe(self, img: np.ndarray, *args, **kwargs) -> pd.DataFrame:
        if img is None:
            raise ValueError("Input image cannot be None")

        return self.run_ocr_to_box(img, *args, **kwargs).to_dataframe()

    @staticmethod
    def get_by_name(backend_name: str) -> 'OCRBackend':
        return get_subclass_by_name(OCRBackend, backend_name)()


class OCRBackendException(Exception):
    pass
