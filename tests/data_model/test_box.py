import math
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict
from copy import deepcopy
import pandas as pd

from mim_ocr.data_model.box import BoxType, Box

INPUT_DATA = {
    "example_tesseract_dataframe1_xlsx_path": "tests/input_data/example_tesseract_dataframe.xlsx",
    "example_box_excel_file": "tests/input_data/example_box_dataframe.xlsx",
    "example_box_excel_file2": "tests/input_data/example_box_dataframe2.xlsx",
    "example_box_csv_file": "tests/input_data/example_box_dataframe.csv",
    "example_text_1": '12 Ala +48 668131234',
    "example_text_2": '4 Wojskowy Szpital Kliniczny z Polikliniką Samodzielny zny Zakład Opieki Zdrowotnej',
    "example_idrs_json": 'tests/input_data/example_idrs_box.json',
}


def assert_equal_dicts(expected: Dict, actual: Dict):
    assert set(actual.keys()) == set(expected.keys())
    for key, exp in expected.items():
        act = actual[key]
        if isinstance(exp, float):
            assert math.isclose(act, exp, rel_tol=1e-6)
        else:
            assert act == exp


def test_preorder_traversal(validate_cwd):
    dataframe_path = INPUT_DATA["example_box_excel_file"]
    box = Box.from_excel(dataframe_path)
    box_type_values = [b.box_type.value for b in box.preorder_traversal()]
    assert box_type_values == [0, 1, 2, 3, 4, 5, 2, 3, 4, 5, 5]


def test_from_and_to_dataframe(validate_cwd):
    dataframe_path = INPUT_DATA["example_box_excel_file"]
    df = pd.read_excel(dataframe_path, keep_default_na=False, dtype={"text": str})
    df.rename(columns={list(df)[0]: 'box_id'}, inplace=True)
    df = df.astype({'box_id': 'str'})
    df.set_index('box_id', inplace=True)
    box = Box.from_excel(dataframe_path)
    df2 = box.to_dataframe()
    assert df.columns.values.tolist() == df2.columns.values.tolist()
    assert list(df.index.values) == list(df2.index.values)
    assert all(df == df2)
    assert box.to_dataframe().iloc[0].box_type == 1
    assert box.to_dataframe().iloc[-1].box_type == 5


def full_assert_box_identity(box1: Box, box2: Box):
    df1 = box1.to_dataframe()
    df2 = box2.to_dataframe()
    assert df1.columns.values.tolist() == df2.columns.values.tolist()
    assert list(df1.index.values) == list(df2.index.values)
    assert all(df1 == df2)
    assert box2.to_list() == box1.to_list()
    assert box2 == box1


def test_to_dataframe_with_additional_data(validate_cwd):
    dataframe_path = INPUT_DATA["example_box_excel_file2"]
    df = pd.read_excel(dataframe_path, keep_default_na=False, dtype={"text": str})
    box = Box.from_excel(dataframe_path)
    df.rename(columns={list(df)[0]: 'box_id'}, inplace=True)
    df = df.astype({'box_id': 'str'})
    df.set_index('box_id', inplace=True)
    with NamedTemporaryFile(suffix="csv") as tmp:
        tmp_path = tmp.name
        box.to_csv(tmp_path)
        box2 = Box.from_csv(Path(tmp_path))
        full_assert_box_identity(box, box2)

    with NamedTemporaryFile(suffix=".xlsx") as tmp:
        tmp_path2 = tmp.name
        box.to_excel(tmp_path2)
        box3 = Box.from_excel(tmp_path2)
        full_assert_box_identity(box, box3)


def test_get_subboxes(validate_cwd):
    dataframe_path = INPUT_DATA["example_box_excel_file"]
    box = Box.from_excel(dataframe_path)
    lv1_box = box.children[0]
    lv4_box_0 = lv1_box.children[0].children[0].children[0]
    lv4_box_1 = lv1_box.children[1].children[0].children[0]
    assert [b.box_type.value for b in lv1_box.get_subboxes()] == [2, 3, 4, 5, 2, 3, 4, 5, 5]
    assert lv1_box.get_subboxes(box_type=BoxType.TESSERACT_LINE) == [lv4_box_0, lv4_box_1]


def test_calc_confidence(validate_cwd):
    dataframe_path = INPUT_DATA["example_box_excel_file"]
    box = Box.from_excel(dataframe_path)
    expected = {
            'avg_confidence': 95.0,
            'total_letters': 18,
            'avg_letters_per_box': 6.0,
    }
    assert_equal_dicts(expected, box.calc_confidence())


def test_calc_confidence_root_box():
    box = Box.create_root_box()
    expected = {
            'avg_confidence': 0.0,
            'total_letters': 0.0,
            'avg_letters_per_box': 0.0,
    }
    assert_equal_dicts(expected, box.calc_confidence())


def test_from_csv(validate_cwd):
    file_path = INPUT_DATA["example_box_csv_file"]
    box = Box.from_csv(file_path)
    assert isinstance(box, Box)
    assert len([b for b in box.preorder_traversal()]) == 36
    assert len(box.get_subboxes(BoxType.TESSERACT_WORD)) == 17
    assert box.get_full_text().strip() == INPUT_DATA["example_text_2"]


def test_from_excel(validate_cwd):
    file_path = INPUT_DATA["example_box_excel_file"]
    box = Box.from_excel(file_path)
    assert isinstance(box, Box)
    assert len([b for b in box.preorder_traversal()]) == 11
    assert len(box.get_subboxes(BoxType.TESSERACT_WORD)) == 3
    assert box.get_full_text().strip() == INPUT_DATA["example_text_1"]


def test_full_box_height_width(validate_cwd):
    file_path = INPUT_DATA["example_box_excel_file"]
    box = Box.from_excel(file_path)
    assert box.full_box_height() == 3530
    assert box.full_box_width() == 2512


def test_add_pages(validate_cwd):
    box = Box.from_idrs_json_path(Path(INPUT_DATA["example_idrs_json"]))
    box.add_pages([deepcopy(box)])
    assert len(box.children) == 2
    assert all(page_box.box_type == BoxType.PREDICTED_PAGE for page_box in box.children)
    assert all(box.children[i].additional_data["page_number"] == i for i in range(len(box.children)))
    assert box.children[1].get_full_text() == "c1-13:6"


def test_merge_subboxes(validate_cwd):
    box = Box.create_root_box()
    word1_box = Box(left=10, top=20, right=30, bottom=25, conf=100, text="t1", box_type=BoxType.IDRS_WORD)
    Box.add_child(box, word1_box,)
    word2_box = Box(left=110, top=120, right=130, bottom=125, conf=50, text="t2", box_type=BoxType.IDRS_WORD)
    Box.add_child(box, word2_box)

    box.merge_subboxes(0, 1)

    assert len(box.children) == 1
    word_box = box.children[0]
    assert word_box.left == 10
    assert word_box.top == 20
    assert word_box.right == 130
    assert word_box.bottom == 125
    assert word_box.conf == 100
    assert word_box.text == "t1t2"
