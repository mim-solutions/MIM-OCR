import json
import re
import uuid
import jsonpickle
from enum import Enum
from pathlib import Path
from os import PathLike
from typing import Dict, List, Tuple, Optional, Iterator, Any, Union

import cv2
import numpy as np
import pandas as pd
from pptree import pptree


class BoxType(Enum):
    ROOT_BOX = 0
    TESSERACT_DOCUMENT = 1
    TESSERACT_PAGE = 2
    TESSERACT_PARAGRAPH = 3
    TESSERACT_LINE = 4
    TESSERACT_WORD = 5
    EASYOCR_BOX = 6
    GCP_DOCUMENT = 17
    # GCP_BLOCK_PICTURE = 18  # TODO:
    # GCP_BLOCK_RULER = 19  # TODO:
    GCP_BLOCK_TABLE = 20
    GCP_BLOCK_TEXT = 21
    # GCP_BLOCK_UNKNOWN = 22  # TODO:
    # GCP_BLOCK_BARCODE = 23  # TODO:
    GCP_BLOCK_PARAGRAPH = 24
    GCP_BLOCK_WORD = 25
    CUSTOM = 30
    PREDICTED_PAGE = 90
    AWS_BLOCK_PAGE = 100
    AWS_BLOCK_LINE = 101
    AWS_BLOCK_WORD = 102


PRECEDING_BOX_TYPES: Dict[BoxType, Optional[BoxType]] = {
    BoxType.ROOT_BOX: None,
    BoxType.TESSERACT_DOCUMENT: BoxType.ROOT_BOX,
    BoxType.TESSERACT_PAGE: BoxType.TESSERACT_DOCUMENT,
    BoxType.TESSERACT_PARAGRAPH: BoxType.TESSERACT_PAGE,
    BoxType.TESSERACT_LINE: BoxType.TESSERACT_PARAGRAPH,
    BoxType.TESSERACT_WORD: BoxType.TESSERACT_LINE,
    BoxType.PREDICTED_PAGE: BoxType.ROOT_BOX,
    BoxType.GCP_DOCUMENT: BoxType.ROOT_BOX,
    BoxType.GCP_BLOCK_TEXT: BoxType.GCP_DOCUMENT,
    BoxType.GCP_BLOCK_PARAGRAPH: BoxType.GCP_BLOCK_TEXT,
    BoxType.GCP_BLOCK_WORD: BoxType.GCP_BLOCK_PARAGRAPH,
}


class Box:
    def __init__(self,
                 text: Optional[str],
                 box_type: BoxType,
                 conf: Optional[float] = None,
                 left: int = 0, top: int = 0, right: int = 0, bottom: int = 0,
                 parent: Optional['Box'] = None,
                 additional_data: Optional[Dict[str, Any]] = None,
                 box_id: Optional[str] = None,
                 ) -> None:
        """
        The main class for storing OCR results.

        The objects represents boxes with text. Thanks to 'parent' parameter the boxes can be
        structured into tree.

        Args:
            conf (Optional[float]): A confidence of OCR (between 0 and 100)
            additional_data (Optional[Dict[str, Any]]): dictionary with extra data associated with node.
            box_id: Optional unique identifier. Useful to identify e.x.
                    words after saving box to disk in batch processing
        """
        if box_type == BoxType.ROOT_BOX:
            self.box_id = None
        elif box_id is None:
            self.box_id = str(uuid.uuid4())
        else:
            self.box_id = str(box_id)
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.conf = conf
        self.text = text or ''
        self.box_type = box_type
        self.children: List['Box'] = []
        self.parent = parent
        self.additional_data = additional_data if additional_data is not None else {}

        # dictionary allowing to quickly access any box using its id will be filled only for ROOT_BOX
        self.box_dict: Optional[Dict[int, 'Box']] = None
        if box_type == BoxType.ROOT_BOX:
            self.box_dict = {}

    def __repr__(self) -> str:
        return (f"Rect(left={self.left}, top={self.top}, right={self.right}, bottom={self.bottom}), "
                f"Text: '{self.text}', BoxType: {self.box_type}, n_children={len(self.children)}")

    __str__ = __repr__

    def __eq__(self, other):
        if self.to_dict() != other.to_dict():
            return False
        return self.children == other.children

    def height(self) -> int:
        return self.bottom - self.top

    def width(self) -> int:
        return self.right - self.left

    def size(self) -> Tuple[int, int]:
        return self.width(), self.height()

    def print(self):
        return pptree.pptree(self)

    def draw_border(self, img: np.ndarray, color: Union[Tuple[int, int, int], List[int]]) -> np.ndarray:
        return cv2.rectangle(img, (self.left, self.top), (self.right, self.bottom), color=color)

    def preorder_traversal(self) -> Iterator['Box']:

        yield self
        for child in self.children:
            for box in child.preorder_traversal():
                yield box

    def reverse_order_traversal(self) -> Iterator['Box']:
        for child in self.children[::-1]:
            for box in child.reverse_order_traversal():
                yield box
        yield self

    def add_box_based_on_type(self, added_box: 'Box') -> None:
        """Add a new box to tree with a parent based on box type"""

        added_type = added_box.box_type
        preceding_type = PRECEDING_BOX_TYPES[added_type]

        for box in self.reverse_order_traversal():
            box_type = box.box_type
            if box_type == preceding_type:
                Box.add_child(box, added_box)
                return
        raise ValueError("Unable to insert box. No suitable parent box found.")

    def calc_confidence(self) -> Dict[str, float]:
        """Returns dict with confidence statistics of words in boxes:
           avg_confidence, total_letters, avg_letters_per_box."""

        df = self.to_dataframe()
        if df.empty:
            return {
                'avg_confidence': 0.0,
                'total_letters': 0.0,
                'avg_letters_per_box': 0.0,
            }
        df = df[df['has_children'] == 0]
        total_letters = df['text'].str.len().sum()
        total_boxes = len(df)
        avg_confidence_weighted_by_text_lengths = (df['conf'] * df['text'].str.len()).sum() / (total_letters or 1)
        return {
            'avg_confidence': avg_confidence_weighted_by_text_lengths,
            'total_letters': total_letters,
            'avg_letters_per_box': total_letters / (total_boxes or 1)
        }

    def to_dict(self) -> Dict:
        d = {
            'left': self.left,
            'top': self.top,
            'right': self.right,
            'bottom': self.bottom,
            'conf': self.conf,
            'text': self.text or '',
            'has_children': len(self.children) > 0,
            'box_type': self.box_type.value,
            'box_id': self.box_id,
        }
        d.update(self.additional_data)
        return d

    def to_json_file(self, output_path: Union[PathLike, str]) -> None:
        json_string = jsonpickle.encode(self)
        # before exporting, we convert json_string to json_object, so the output file can be easily read by human
        json_object = json.loads(json_string)
        with open(output_path, 'w') as output_file:
            json.dump(json_object, output_file, indent=2)

    @staticmethod
    def from_json_file(input_path: Union[PathLike, str]) -> 'Box':
        with open(input_path) as input_file:
            input_data = json.load(input_file)
        input_json_string = json.dumps(input_data)
        return Box.from_json_str(input_json_string)

    @staticmethod
    def from_json_str(input_json_string: str):
        box = jsonpickle.decode(input_json_string)
        box._recalculate_box_dict()
        return box

    def _recalculate_box_dict(self):
        if self.box_type != BoxType.ROOT_BOX:
            raise ValueError("You can recalculate box_dict only for Root Box.")
        self.box_dict = {b.box_id: b for b in self.preorder_traversal()}

    def to_dataframe(self) -> pd.DataFrame:
        if self.box_type == BoxType.ROOT_BOX and not self.children:
            return pd.DataFrame(columns=["left", "right", "bottom", "top", "conf", "text", "has_children", "box_type"])
        df = pd.DataFrame.from_records(self.to_list())
        df.set_index("box_id", inplace=True)
        return df

    def to_list(self) -> List[Dict]:
        return [b.to_dict() for b in self.preorder_traversal() if (b.box_type != BoxType.ROOT_BOX)]

    def to_csv(self, path: str) -> None:
        self.to_dataframe().to_csv(path)

    def to_excel(self, path: str) -> None:
        self.to_dataframe().to_excel(path)

    @staticmethod
    def create_root_box() -> 'Box':
        """Creates dummy box with no dimensions, text, confidence etc. that will be a root for real boxes"""
        return Box(left=-1, top=-1, right=-1, bottom=-1, conf=-1,
                   text=None, box_type=BoxType.ROOT_BOX, parent=None)

    @staticmethod
    def create_page_box(page_number: int = 0, page_size: Tuple[int, int] = None) -> 'Box':
        return Box(left=-1, top=-1, right=-1, bottom=-1, conf=-1,
                   text=None, box_type=BoxType.PREDICTED_PAGE, parent=None,
                   additional_data={"page_number": page_number, "page_size": page_size})

    def get_subboxes(self, box_type: Optional[BoxType] = None) -> List['Box']:
        """
        returns list of subboxes with given type
        if type is not specified all subboxes are returned
        """
        box_iterator = self.preorder_traversal()
        next(box_iterator)
        if box_type:
            return [box for box in box_iterator if box.box_type == box_type]
        return [box for box in box_iterator]

    @staticmethod
    def add_child(parent: 'Box', child: 'Box') -> None:
        parent.children.append(child)
        child.parent = parent
        root_box = parent.get_root()
        for box in child.preorder_traversal():
            if box.box_type == BoxType.ROOT_BOX:
                raise ValueError("You cannot have two root boxes in one tree")
            root_box.box_dict[box.box_id] = box

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> 'Box':
        """
        create Box from pandas DataFrame
        required index: it will be used as box_id
        required columns (at the beginning):
            left: int
            top: int
            right: int
            bottom: int
            conf: float
            box_type: int - compatible with BoxType enum
        optional columns:
            : values of additional data. might be an integer, float or a string.
        """
        fixed_columns = ['left', 'top', 'right', 'bottom', 'conf', 'text', 'has_children', 'box_type']
        assert set(list(df.columns)[:len(fixed_columns)]) == set(fixed_columns)

        for colname in fixed_columns:
            assert colname in df.columns

        additional_columns_names = list(df.columns)[len(fixed_columns):]

        tree = Box.create_root_box()
        for index, row in df.iterrows():
            additional_data = {column_name: row[column_name] for column_name in additional_columns_names}
            new_box = Box(left=row.left, top=row.top, right=row.right, bottom=row.bottom,
                          conf=row.conf,
                          text=row.text,
                          box_type=BoxType(row.box_type),
                          box_id=index,
                          additional_data=additional_data)
            tree.add_box_based_on_type(new_box)

        return tree

    @staticmethod
    def from_excel(path: Path) -> 'Box':
        df = pd.read_excel(path, keep_default_na=False, index_col=0, converters={0: str, "text": str})
        return Box.from_dataframe(df)

    @staticmethod
    def from_csv(path: Path) -> 'Box':
        df = pd.read_csv(
            path, keep_default_na=False, index_col=0,
            converters={0: str, "text": str}, on_bad_lines="warn")
        return Box.from_dataframe(df)

    def add_pages(self, boxes: List['Box']):
        '''Append PREDICTED_PAGE boxes present as children of input boxes.'''
        for box in boxes:
            for page_box in box.children:
                if page_box.box_type != BoxType.PREDICTED_PAGE:
                    raise ValueError("Wrong box format.")
                page_box.additional_data['page_number'] = len(self.children)
                self.add_child(self, page_box)

    def get_full_text(self):
        return " ".join([b.text for b in self.preorder_traversal() if b.text])

    def get_root(self) -> 'Box':
        if not self.parent:
            return self
        return self.parent.get_root()

    def get_ancestor_box_additional_data(self, additional_data_key: str) -> Tuple[int, int]:
        """
        If the box has additional_data_key in it's additional_data, returns the value attached to it.
        Else, returns such value of it's closest ancestor or None.
        """
        if additional_data_key in self.additional_data:
            return self.additional_data[additional_data_key]
        if self.parent is not None:
            return self.parent.get_ancestor_box_additional_data(additional_data_key)
        return None

    def full_box_height(self) -> int:
        min_full_bot_top = min([b.top for b in self.preorder_traversal() if b.box_type != BoxType.ROOT_BOX])
        max_full_box_bottom = max([b.bottom for b in self.preorder_traversal() if b.box_type != BoxType.ROOT_BOX])
        return max_full_box_bottom - min_full_bot_top

    def full_box_width(self) -> int:
        min_full_box_left = min([b.left for b in self.preorder_traversal() if b.box_type != BoxType.ROOT_BOX])
        max_full_box_right = max([b.right for b in self.preorder_traversal() if b.box_type != BoxType.ROOT_BOX])
        return max_full_box_right - min_full_box_left

    def has_any_text(self) -> bool:
        return bool(re.search(r"\S", self.get_full_text()))

    def box_number_in_parent(self) -> int:
        """Returns the position of box in tree among siblings"""
        if not self.parent:
            return 0
        position = 0
        while self.parent.children[position] is not self:
            position += 1

        return position

    @property
    def feature(self) -> Optional[str]:
        return self.additional_data.get("feature")

    @property
    def main_feature(self) -> Optional[str]:
        if not self.additional_data.get("feature"):
            return None
        return self.additional_data["feature"].rstrip("<->")

    def get_subbox_by_id(self, box_id: str) -> 'Box':
        for b in self.preorder_traversal():
            if b.box_id == box_id:
                return b
        raise ValueError("Box with given id not found")

    def merge_subboxes(self, i: int, j: int):
        """merge two child boxes"""
        child1 = self.children[i]
        child2 = self.children[j]

        child1.text = child1.text + child2.text
        child1.left = min(child1.left, child2.left)
        child1.right = max(child1.right, child2.right)
        child1.top = min(child1.top, child2.top)
        child1.bottom = max(child1.bottom, child2.bottom)

        del self.children[j]
