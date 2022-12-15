from typing import List
from pytest import mark

from mim_ocr.data_model import Box
from mim_ocr.data_model.box import BoxType
from mim_ocr.heuristics import Occurrence
from mim_ocr.heuristics import KeywordFeature
from mim_ocr.heuristics.heuristic_analysis import _fill_box_with_feature_occurrences, heuristic_examine_box_lines
from mim_ocr.backends import TesseractBackend, AwsTextractBackend, GCPBackend
from mim_ocr.image import open_image
from mim_ocr.heuristics import basic_features


def mocked_get_feature_priority_by_name(name: str) -> int:
    name = name.rstrip("<->")
    if name == "Feature1":
        return 8
    if name == "Feature2":
        return 7
    raise ValueError(f"Cannot determine priority for {name} feature occurrence.")


def create_box_with_words(words: List[str]) -> Box:
    box = Box.create_root_box()
    line_box = Box(text=None, box_type=BoxType.IDRS_LINE)
    Box.add_child(box, line_box)
    for word in words:
        word_box = Box(text=word, box_type=BoxType.IDRS_WORD)
        Box.add_child(line_box, word_box)
    return box


def test_fill_box_with_feature_occurrences_one_word_feature(mocker):
    mocker.patch("mim_ocr.heuristics.feature.Feature.get_feature_priority_by_name",
                 mocked_get_feature_priority_by_name)

    box = create_box_with_words(["aaaaa", "bbb"])

    occurrences = [
        Occurrence(
            full_text='bbb', feature_name='Feature1', start=6,
            end=9, matched_text='bbb', priority=8),
    ]

    line_box = box.children[0]
    _fill_box_with_feature_occurrences(line_box, occurrences)

    assert line_box.children[0].feature is None
    assert line_box.children[1].feature == 'Feature1'


def test_fill_box_with_feature_occurrences_one_word_feature_priority(mocker):
    mocker.patch("mim_ocr.heuristics.feature.Feature.get_feature_priority_by_name",
                 mocked_get_feature_priority_by_name)

    box = create_box_with_words(["aaaaa", "bbb"])

    occurrences = [
        Occurrence(
            full_text='bbb', feature_name='Feature2', start=6,
            end=9, matched_text='bbb', priority=7),
        Occurrence(
            full_text='bbb', feature_name='Feature1', start=6,
            end=9, matched_text='bbb', priority=8),
    ]

    line_box = box.children[0]
    _fill_box_with_feature_occurrences(line_box, occurrences)

    assert line_box.children[0].feature is None
    assert line_box.children[1].feature == 'Feature1'


def test_fill_box_with_feature_occurrences_two_lines(mocker):
    mocker.patch("mim_ocr.heuristics.feature.Feature.get_feature_priority_by_name",
                 mocked_get_feature_priority_by_name)

    box = create_box_with_words(["%", "bazocytów", "C"])

    occurrences = [
        Occurrence(
            full_text='% bazocytów C', feature_name='Feature1', start=0,
            end=12, matched_text='% bazocytów C', priority=7),
    ]

    line_box = box.children[0]
    _fill_box_with_feature_occurrences(line_box, occurrences)

    assert line_box.children[0].feature == "Feature1<-"
    assert line_box.children[1].feature == "Feature1-"
    assert line_box.children[2].feature == 'Feature1->'


def test_fill_box_with_feature_occurrences_two_lines_priority(mocker):
    mocker.patch("mim_ocr.heuristics.feature.Feature.get_feature_priority_by_name",
                 mocked_get_feature_priority_by_name)

    box = create_box_with_words(["%", "bazocytów", "C"])

    occurrences = [
        Occurrence(
            full_text='% bazocytów C', feature_name='Feature1', start=0,
            end=12, matched_text='% bazocytów C', priority=8),
        Occurrence(
            full_text='C', feature_name='Feature2', start=11,
            end=12, matched_text='C', priority=7),
    ]

    line_box = box.children[0]
    _fill_box_with_feature_occurrences(line_box, occurrences)

    assert line_box.children[0].feature == "Feature1<-"
    assert line_box.children[1].feature == "Feature1-"
    assert line_box.children[2].feature == 'Feature1->'


def test_heuristic_examine_box_lines_two_words(mocker):
    Feature1 = KeywordFeature(
        "Feature1", ["one two"],
        allow_upper=False,
        allow_first_letter_upper=False,
        allow_recompute=True,
    )

    mocker.patch("mim_ocr.heuristics.feature.Feature.get_feature_priority_by_name",
                 mocked_get_feature_priority_by_name)

    box = create_box_with_words(["one", "two"])
    line_box = box.children[0]

    heuristic_examine_box_lines(box, [Feature1])

    assert line_box.children[0].feature == "Feature1<-"
    assert line_box.children[1].feature == "Feature1->"


def test_heuristic_examine_box_lines_two_words_upper(mocker):
    Feature1 = KeywordFeature(
        "Feature1", ["one two"],
        allow_upper=True,
        allow_first_letter_upper=False,
        allow_recompute=True,
    )

    mocker.patch("mim_ocr.heuristics.feature.Feature.get_feature_priority_by_name",
                 mocked_get_feature_priority_by_name)

    box = create_box_with_words(["ONE", "TWO"])
    line_box = box.children[0]

    heuristic_examine_box_lines(box, [Feature1])

    assert line_box.children[0].feature == "Feature1<-"
    assert line_box.children[1].feature == "Feature1->"


def test_heuristic_examine_box_lines_two_words_first_letter_upper(mocker):
    Feature1 = KeywordFeature(
        "Feature1", ["one two"],
        allow_upper=False,
        allow_first_letter_upper=True,
        allow_recompute=True,
    )

    mocker.patch("mim_ocr.heuristics.feature.Feature.get_feature_priority_by_name",
                 mocked_get_feature_priority_by_name)

    box = create_box_with_words(["One", "two"])
    line_box = box.children[0]

    heuristic_examine_box_lines(box, [Feature1])

    assert line_box.children[0].feature == "Feature1<-"
    assert line_box.children[1].feature == "Feature1->"


@mark.parametrize('backend', [TesseractBackend(), AwsTextractBackend(), GCPBackend()])
def test_heuristic_examine_box_lines_on_backends_ocr_data(backend):
    def pred(b):
        return b['text'] == '2016-10-12' and b['feature'] == 'Date'

    path = 'tests/input_data/example_report1.png'
    img = open_image(path)
    box = backend.run_ocr_to_box(img)
    heuristic_examine_box_lines(box, [basic_features.DATE_FEATURE])
    matches = sum(map(pred, box.to_list()))
    assert matches == 4
