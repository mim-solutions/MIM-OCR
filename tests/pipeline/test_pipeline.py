import os
import string
import tempfile
from pathlib import Path
import random
from typing import Any, Dict

import numpy as np
from pytest import raises

from mim_ocr.backends import TesseractBackend
from mim_ocr.data_model import Box
from mim_ocr.excepions.smooth_job_context import SmoothOCRJobRunContext
from mim_ocr.heuristics import NUMBER_FEATURE, PHONE_NUMBER_FEATURE, DATE_FEATURE
from mim_ocr.image import open_image
from mim_ocr.image.transformations import reorient, deskew
from mim_ocr.pipeline.pipeline import run_ocr_pipeline_on_file, run_pipeline_and_save_results_to_file, \
    RunPipelineAndSaveResultToFileInput

input_image_path = "tests/input_data/example_report1-reorient90.png"
box_path = "tests/input_data/example_box_json.json"


def fail_transform(img: np.ndarray, path: Path, metadata: Dict[str, Any]) -> np.ndarray:
    raise ValueError("Some error")


def test_fail_pipeline(validate_cwd):
    with raises(ValueError):
        run_ocr_pipeline_on_file(input_path=Path(input_image_path), preprocessing_transformations=[fail_transform],
                                 backend=TesseractBackend())


def test_suppress_exceptions_pipeline(validate_cwd):
    with SmoothOCRJobRunContext(job_info="", suppress_exceptions=True):
        run_ocr_pipeline_on_file(input_path=Path(input_image_path), preprocessing_transformations=[fail_transform],
                                 backend=TesseractBackend(), suppress_exceptions=True)


def test_run_pipeline_and_save_results_to_file_img(validate_cwd):
    with tempfile.NamedTemporaryFile(suffix=".json") as output_tmp_file:
        tmp_file_name = output_tmp_file.name

        with tempfile.NamedTemporaryFile(suffix=".png") as preprocessed_tmp_file:
            preprocessed_tmp_file_name = preprocessed_tmp_file.name

            args = [RunPipelineAndSaveResultToFileInput(
                output_path=tmp_file_name,
                image_input_path=Path(input_image_path),
                preprocessed_image_path=Path(preprocessed_tmp_file_name),
                preprocessing_transformations=[reorient, deskew],
                backend=TesseractBackend(),
                features=[NUMBER_FEATURE, PHONE_NUMBER_FEATURE, DATE_FEATURE]
            )]
            run_pipeline_and_save_results_to_file(args)

            assert Box.from_json_file(tmp_file_name)
            assert open_image(preprocessed_tmp_file_name).any()


def test_run_pipeline_and_save_results_to_file_box(validate_cwd):
    output_tmpfilename = 'mim_ocr_test_' + ''.join(random.choice(string.ascii_lowercase) for i in range(10)) + '.json'
    output_path = Path(tempfile.gettempdir()) / output_tmpfilename

    args = [RunPipelineAndSaveResultToFileInput(
        output_path=output_path,
        box_input_path=Path(box_path),
        features=[NUMBER_FEATURE, PHONE_NUMBER_FEATURE, DATE_FEATURE]
    )]

    run_pipeline_and_save_results_to_file(args)

    assert Box.from_json_file(output_path)

    os.remove(output_path)
