import dataclasses
from pathlib import Path
from typing import List, Callable, Optional, Tuple

import cv2
import numpy as np

from mim_ocr.backends import OCRBackend
from mim_ocr.data_model import Box
from mim_ocr.exceptions.smooth_job_context import SmoothOCRJobRunContext
from mim_ocr.heuristics import Feature, heuristic_examine_box_lines
from mim_ocr.image import open_image


def run_ocr_pipeline_on_file(input_path: Path, preprocessing_transformations: List[Callable],
                             backend: Optional[OCRBackend]) -> Tuple[np.ndarray, Optional[Box]]:
    img = open_image(input_path)
    metadata = {'path': input_path}

    for t in preprocessing_transformations:
        img = t(img, input_path, metadata)

    if backend is not None:
        return img, backend.run_ocr_to_box(img)
    else:
        return img, None


@dataclasses.dataclass
class RunPipelineAndSaveResultToFileInput:
    output_path: Optional[Path]
    image_input_path: Optional[Path] = None
    preprocessed_image_path: Optional[Path] = None
    preprocessing_transformations: Optional[List[Callable]] = dataclasses.field(default_factory=lambda: [])
    backend: Optional[OCRBackend] = None
    box_input_path: Optional[Path] = None
    features: List[Feature] = dataclasses.field(default_factory=lambda: [])

    def validate(self):
        if not (self.image_input_path or self.box_input_path):
            raise ValueError("You have to provide image_input_path or box_input_path")
        if self.image_input_path and not self.backend:
            raise ValueError("You have to provide backend")
        if self.box_input_path and (self.image_input_path
                                    or self.preprocessed_image_path
                                    or self.preprocessing_transformations
                                    or self.backend):
            raise ValueError("You cannot use image_input_path or preprocessed_image_path "
                             "or preprocessing_transformations or backend when using precomputed boxes.")
        if self.box_input_path and not self.output_path:
            raise ValueError("You need to specify output path when using precomputed boxes")
        if self.box_input_path and not self.features:
            raise ValueError("No features defined, nothing to do.")

    def read_box(self) -> Box:
        if str(self.box_input_path).endswith('.json'):
            return Box.from_json_file(self.box_input_path)
        if str(self.box_input_path).endswith('.xlsx'):
            return Box.from_excel(self.box_input_path)
        if str(self.box_input_path).endswith('.csv'):
            return Box.from_csv(self.box_input_path)
        raise ValueError("Unrecognized Box file format.")


def run_pipeline_and_save_results_to_file(args_list: List[RunPipelineAndSaveResultToFileInput],
                                          suppress_exceptions: bool = False,
                                          job_info: str = "") -> None:
    """Run full pipeline for an image file.
    Args:
        output_path (Optional[pathlib.Path]): path to output excel file for OCR results
        image_input_path (Optional[pathlib.Path]): path to input image file if pipeline runs on image
        preprocessed_image_path (Optional[pathlib.Path]): path to store preprocessed image
        preprocessing_transformations (List[Callable]): list of image preprocessing transformations
        backend (OCRBackend): if None, then OCR is not performed
        box_input_path (Optional[pathlib.Path]): path to input box file if pipeline runs on box images
        features (Optional[List[Feature]]): Space-separated list of names of Feateres to search in OCR results, example:
                                             NUMBER_FEATURE PHONE_NUMBER_FEATURE NER_FEATURE.
        suppress_exceptions (bool): allows to log and not raise every exception e.g. for batch runs
        job_info (str): additional info for logs
    """
    for args in args_list:
        with SmoothOCRJobRunContext(job_info=job_info, suppress_exceptions=suppress_exceptions):
            args.validate()

            if args.image_input_path:
                img, box = run_ocr_pipeline_on_file(
                    args.image_input_path,
                    args.preprocessing_transformations,
                    args.backend)
                if args.preprocessed_image_path:
                    cv2.imwrite(str(args.preprocessed_image_path), img)

            if args.box_input_path:
                box = args.read_box()

            if args.output_path and args.features:
                heuristic_examine_box_lines(box, features_to_check=args.features)

            if box and args.output_path:
                box.to_json_file(args.output_path)
