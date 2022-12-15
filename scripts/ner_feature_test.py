from pathlib import Path

from mim_ocr.data_model import Box


from mim_ocr.heuristics import heuristic_examine_box_lines
from mim_ocr.optional_elements.ner_feature import NER_FEATURE

box = Box.from_excel(
    Path("/home/jerzy/PycharmProjects/MiM/mim_ocr/sample_data/sample_data_tesseract_result/canvas.png.xlsx"))

heuristic_examine_box_lines(box, [NER_FEATURE])
