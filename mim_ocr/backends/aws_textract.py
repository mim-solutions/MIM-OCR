from typing import Tuple

import boto3
import numpy as np
import cv2

from mim_ocr.backends import OCRBackend
from mim_ocr.data_model import Box
from mim_ocr.data_model.box import BoxType


class AwsTextractBackend(OCRBackend):

    def run_ocr_to_box(self, img: np.ndarray, *args, **kwargs) -> Box:
        client = boto3.client('textract')
        img_height, img_width = img.shape[0], img.shape[1]
        img2 = cv2.imencode('.png', img)[1]
        response = client.detect_document_text(Document={'Bytes': img2.tobytes()})
        return self.response_to_box(response, img_height, img_width)

    def response_to_box(self, response: dict, img_height: int, img_width: int) -> Box:
        root_box = Box.create_root_box()
        root_box.additional_data = {'DocumentMetadata': response['DocumentMetadata']}

        pages = [b for b in response['Blocks'] if b['BlockType'] == 'PAGE']
        lines = [b for b in response['Blocks'] if b['BlockType'] == 'LINE']
        words = [b for b in response['Blocks'] if b['BlockType'] == 'WORD']

        for page in pages:
            page_box = Box(conf=None, text=None, box_type=BoxType.AWS_BLOCK_PAGE)
            Box.add_child(root_box, page_box)

            child_lines = [line for line in lines if line['Id'] in page['Relationships'][0]['Ids']]
            for line in child_lines:
                left, top, right, bottom = self.geometry_to_boundingbox(line, img_height, img_width)
                confidence = line['Confidence']
                line_box = Box(left=left, top=top, right=right, bottom=bottom,
                               conf=confidence, text=None, box_type=BoxType.AWS_BLOCK_LINE)
                Box.add_child(page_box, line_box)

                child_words = [word for word in words if word['Id'] in line['Relationships'][0]['Ids']]
                for word in child_words:
                    confidence = word['Confidence']
                    text = word['Text']
                    left, top, right, bottom = self.geometry_to_boundingbox(word, img_height, img_width)
                    word_box = Box(left=left, top=top, right=right, bottom=bottom,
                                   conf=confidence, text=text, box_type=BoxType.AWS_BLOCK_WORD)
                    Box.add_child(line_box, word_box)
        return root_box

    @staticmethod
    def geometry_to_boundingbox(block: dict, img_height: int, img_width: int) -> Tuple[int, int, int, int]:
        top = img_height * block['Geometry']['BoundingBox']['Top']
        left = img_width * block['Geometry']['BoundingBox']['Left']
        width = img_width * block['Geometry']['BoundingBox']['Width']
        height = img_height * block['Geometry']['BoundingBox']['Height']
        right = left + width
        bottom = top + height

        return int(left), int(top), int(right), int(bottom)
