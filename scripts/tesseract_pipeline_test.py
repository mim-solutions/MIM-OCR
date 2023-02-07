import logging
import os.path
import sys
from os import listdir
from pathlib import Path

import cv2
from pytesseract import TesseractError

from mim_ocr.heuristics import heuristic_examine_box_lines, NUMBER_FEATURE, PHONE_NUMBER_FEATURE
from mim_ocr.preprocessing import deskew_cv2, reorient_cv2
from mim_ocr.backends.tesseract import TesseractBackend
from mim_ocr.visualization import visualize_ocr_result
from mim_ocr.image import open_image

logger = logging.getLogger(__name__)

TESSERACT_CONFIG = r'--oem 1 --psm 3 -l pol'


def heuristics_and_visualize_on_dir(data_dir_path: Path, tesseract_config: str) -> None:
    files = [f for f in listdir(data_dir_path) if os.path.isfile(
        os.path.join(data_dir_path, f))]

    backend = TesseractBackend()

    i = 0
    while True:
        if i >= len(files):
            break
        path = os.path.join(data_dir_path, files[i])
        print(path)
        img_metadata = {
            'path': path
        }

        img_org = open_image(path)

        box = backend.run_ocr_to_box(img_org, config=tesseract_config)
        img_metadata['quality_org'] = f"{box.calc_confidence()['avg_confidence']:.2}"

        # reorientation
        try:
            img, orientation = reorient_cv2(img_org, path)
            img_metadata['orientation'] = orientation

            box = backend.run_ocr_to_box(img, config=tesseract_config)
            img_metadata['quality_reorient'] = f"{box.calc_confidence()['avg_confidence']:.2}"
        except TesseractError:
            logger.warning(
                "Tesseract Error, cannot determine image orientation.")
            i += 1
            continue

        # deskew (rotation)
        img, angle = deskew_cv2(img)
        img_metadata['angle'] = f"{angle:.2}"

        box = backend.run_ocr_to_box(img, config=tesseract_config)
        img_metadata['quality'] = f"{box.calc_confidence()['avg_confidence']:.2}"

        heuristic_examine_box_lines(box, [NUMBER_FEATURE, PHONE_NUMBER_FEATURE])

        # visualize
        visualisation_image = visualize_ocr_result(
            original_image=img,
            box=box,
            metadata=img_metadata,
            show_confidence=False,
            additional_value_to_show='feature',
            show_only_text_with_additional_value=False,
            # only_ocr_result=True,
            only_original=True,
        )

        cv2.namedWindow("OCR result", cv2.WINDOW_NORMAL)
        cv2.imshow("OCR result", visualisation_image)
        k = cv2.waitKey(0)

        if k == 27:  # Esc - close
            break
        elif k in (119, 97) and i > 0:  # "w" and "a" - go back
            i -= 1
        else:
            i += 1
            if i == len(files):
                break


if __name__ == "__main__":
    dirname = sys.argv[1]
    heuristics_and_visualize_on_dir(
        data_dir_path=Path(dirname), tesseract_config=TESSERACT_CONFIG)
