import itertools
from typing import List, Optional

from mim_ocr.data_model import Box
from .feature import Occurrence, Feature
from ..data_model.box import BoxType


def heuristic_examine_box_lines(box: Box, features_to_check: Optional[List[Feature]] = None) -> None:
    """
    Find features for box elements and store information in additional Data.
    Found features are added to additional_data field of the analyzed box.
    Args:
        box: Box
        features_to_check: list of feature that will be checked
    """
    if features_to_check is None:
        features_to_check = []

    if not features_to_check:
        raise ValueError("Feature list required")

    for b in box.preorder_traversal():
        b.additional_data['feature'] = b.additional_data.get('feature', None)
        if b.box_type not in [BoxType.TESSERACT_LINE, BoxType.AWS_BLOCK_LINE, BoxType.GCP_BLOCK_PARAGRAPH]:
            continue
        text = b.get_full_text()
        occurrences = find_heuristic_features(text, features_to_check)
        if occurrences:
            _fill_box_with_feature_occurrences(b, occurrences)


def find_heuristic_features(original_text: str, features: Optional[List[Feature]] = None) -> List[Occurrence]:
    return list(itertools.chain.from_iterable([feature.find_occurrences(original_text) for feature in features]))


def _fill_box_with_feature_occurrences(tesseract_line_box: Box, feature_occurrences: List[Occurrence]) -> None:
    """As we calculated feature for text lines, we need to map them onto specific words e.g. for visualization"""
    for word_box in tesseract_line_box.children:
        if "feature" not in word_box.additional_data:
            word_box.additional_data["feature"] = None

    for feature_occurrence in sorted(feature_occurrences, key=lambda o: 256*o.priority + o.end - o.start, reverse=True):
        word_position_start = 0
        word_position_end = 0

        for word_box in tesseract_line_box.children:
            word_position_end += len(word_box.text)
            if word_box.feature \
                    and Feature.get_feature_priority_by_name(word_box.feature) >= feature_occurrence.priority:
                pass

            elif feature_occurrence.start >= word_position_start and feature_occurrence.end <= word_position_end:
                word_box.additional_data['feature'] = feature_occurrence.feature_name
            elif feature_occurrence.start < word_position_start <= word_position_end < feature_occurrence.end:
                word_box.additional_data['feature'] = feature_occurrence.feature_name + "-"
            elif word_position_start <= feature_occurrence.start <= word_position_end < feature_occurrence.end:
                word_box.additional_data['feature'] = feature_occurrence.feature_name + "<-"
            elif feature_occurrence.start < word_position_start <= feature_occurrence.end <= word_position_end:
                word_box.additional_data['feature'] = feature_occurrence.feature_name + "->"
            word_position_start = word_position_end = word_position_start + len(word_box.text) + 1
