import gc
from pytest import raises

from mim_ocr.data_model import Box
from mim_ocr.heuristics import (NUMBER_FEATURE, heuristic_examine_box_lines, RegexFeature, Feature)


# check if instances of features in the project have priorities consistent
# with FEATURES_PRIORITIES_DICTIONARY from mim_ocr.heuristics.features_model.py
from mim_ocr.heuristics.feature import FEATURES_PRIORITIES_DICTIONARY


def test_feature_priorities_dictionary_consistency():

    # Feature instances used for testing only and not used in actual pipeline
    temporary_features = ["TestKeyword1", "TestKeyword2", "TestKeyword3", "NumberLowPriority", "NumberHighPriority",
                          "fuzzy feature"]

    found_features_priorities_dictionary = {obj.name: obj.priority for obj in gc.get_objects()
                                            if isinstance(obj, Feature) and obj.name not in temporary_features}

    assert found_features_priorities_dictionary == FEATURES_PRIORITIES_DICTIONARY


def test_features_priorities_mechanism(validate_cwd, mocker):

    def mocked_get_feature_priority_by_name(feature_name: str) -> int:
        if feature_name == "Number":
            return NUMBER_FEATURE.priority
        if feature_name == "NumberLowPriority":
            return 2
        if feature_name == "NumberHighPriority":
            return 19

    mocker.patch("mim_ocr.heuristics.feature.Feature.get_feature_priority_by_name",
                 mocked_get_feature_priority_by_name)

    box = Box.from_excel("tests/input_data/example_box_dataframe.xlsx")
    heuristic_examine_box_lines(box, features_to_check=[NUMBER_FEATURE])
    assert any([b.text == "12" and b.additional_data['feature'] == "Number" for b in box.preorder_traversal()])

    NUMBER_FEATURE_LOW_PRIORITY = RegexFeature(
        name="NumberLowPriority",
        core_regex=r"(?:|>|<|=|>=|<=)\d+(?:(?:\.|,)?)\d+",
        before_regex=r"\s|^",
        after_regex=r"\s|$",
        priority=2)

    heuristic_examine_box_lines(box, features_to_check=[NUMBER_FEATURE_LOW_PRIORITY])
    assert not any([b.text == "12" and b.additional_data['feature'] ==
                    "NumberLowPriority" for b in box.preorder_traversal()])

    NUMBER_FEATURE_HIGH_PRIORITY = RegexFeature(
        name="NumberHighPriority",
        core_regex=r"(?:|>|<|=|>=|<=)\d+(?:(?:\.|,)?)\d+",
        before_regex=r"\s|^",
        after_regex=r"\s|$",
        priority=19)

    heuristic_examine_box_lines(box, features_to_check=[NUMBER_FEATURE_HIGH_PRIORITY])

    assert any([b.text == "12" and b.additional_data['feature'] ==
                "NumberHighPriority" for b in box.preorder_traversal()])


# test feature unpresent in FEATURES_PRIORITIES_DICTIONARY from mim_ocr.heuristics.features_model.py
def test_priority_of_nonexistent_feature(validate_cwd):
    box = Box.from_excel("tests/input_data/example_box_dataframe_with_nonexistent_feature.xlsx")
    with raises(ValueError):
        heuristic_examine_box_lines(box, features_to_check=[NUMBER_FEATURE])
