import itertools
from typing import List, Optional

from mim_ocr.data_model import Box
from mim_ocr.heuristics import Feature, Occurrence


class TextLineAnalysis:
    def __init__(self, original_text: str, features: Optional[List[Feature]] = None):
        if features is None:
            features = []

        self.original_text = original_text
        self.feature_occurrences = list(
            itertools.chain.from_iterable([feature.find_occurrences(self.original_text) for feature in features]))

    def __repr__(self):
        return f"{self.original_text}: {self.feature_occurrences}"

    __str__ = __repr__


def map_features_onto_words(tesseract_line_box: Box, feature_occurrences: List[Occurrence]) -> None:
    """As we calculated feature for text lines, we need to map them onto specific words e.g. for visualization"""
    position = 0
    for word_box in tesseract_line_box.children:
        if word_box.text:
            word_length = len(word_box.text)
            for occurrence in feature_occurrences:
                if position <= occurrence.start < position + word_length:
                    word_box.additional_data = {"feature": occurrence.feature.__name__.replace("Feature", "")}
                    break
            if not word_box.additional_data:
                word_box.additional_data = {"feature": ""}
        position += word_length + 1
