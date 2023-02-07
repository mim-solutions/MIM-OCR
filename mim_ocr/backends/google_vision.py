from typing import Tuple

import cv2
import numpy as np
from google.cloud import vision
from google.cloud.vision_v1 import Word, BoundingPoly

from mim_ocr.backends import OCRBackend
from mim_ocr.data_model import Box
from mim_ocr.data_model.box import BoxType


class GCPBackend(OCRBackend):
    """based on https://github.com/SoloSynth1/gcp-vision-ocr/blob/master/vision.py"""

    def run_ocr_to_box(self, img: np.ndarray, *args, **kwargs) -> Box:

        img_str = cv2.imencode('.png', img)[1].tostring()

        client = vision.ImageAnnotatorClient()

        image = vision.Image(content=img_str)
        response = client.document_text_detection(image=image)
        document = response.full_text_annotation

        # https://cloud.google.com/vision/docs/fulltext-annotations
        root_box = Box.create_root_box()
        for page in document.pages:
            page_box = Box(left=0, top=0, right=page.width, bottom=page.height,
                           conf=None, text=None, box_type=BoxType.GCP_DOCUMENT)
            Box.add_child(root_box, page_box)

            for block in page.blocks:
                # Following block types are supported by Google OCR, but are not parsed by MIM OCR:
                # BlockType.BARCODE
                # BlockType.PICTURE
                # BlockType.RULER
                # BlockType.TABLE
                # BlockType.UNKNOWN
                if block.block_type == block.BlockType.TABLE:
                    box_type = BoxType.GCP_BLOCK_TABLE  # TODO: check whether text extraction for tables works.
                elif block.BlockType.TEXT:
                    box_type = BoxType.GCP_BLOCK_TEXT
                else:
                    continue

                (left, top, right, bottom) = self._get_rectangle_from_bounding_box(block.bounding_box)
                block_box = Box(left=left, top=top, right=right, bottom=bottom,
                                conf=block.confidence*100, text=None, box_type=box_type)
                Box.add_child(page_box, block_box)

                for paragraph in block.paragraphs:
                    (left, top, right, bottom) = self._get_rectangle_from_bounding_box(paragraph.bounding_box)
                    paragraph_box = Box(left=left, top=top, right=right, bottom=bottom,
                                        conf=block.confidence*100, text=None,
                                        box_type=BoxType.GCP_BLOCK_PARAGRAPH)
                    Box.add_child(block_box, paragraph_box)

                    for word in paragraph.words:
                        (left, top, right, bottom) = self._get_rectangle_from_bounding_box(word.bounding_box)
                        text = self._get_text_for_word(word)
                        word_box = Box(left=left, top=top, right=right, bottom=bottom,
                                       conf=block.confidence*100, text=text,
                                       box_type=BoxType.GCP_BLOCK_WORD)
                        Box.add_child(paragraph_box, word_box)
        return root_box

    @staticmethod
    def _get_text_for_word(word: Word) -> str:
        return "".join([symbol.text for symbol in word.symbols])

    @staticmethod
    def _get_rectangle_from_bounding_box(bounding_box: BoundingPoly) -> Tuple[int, int, int, int]:
        y_values = [vertice.y for vertice in bounding_box.vertices]
        x_values = [vertice.x for vertice in bounding_box.vertices]

        return min(x_values), min(y_values), max(x_values), max(y_values)
