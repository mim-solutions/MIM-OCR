import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
import cv2
import loguru
import numpy as np

from mim_ocr import mim_ocr_cfg, mim_ocr_cfg_required
from mim_ocr.backends import OCRBackend, OCRBackendException
from mim_ocr.data_model import Box


class IDRSBackend(OCRBackend):

    def __init__(self, custom_lexicon_path: Optional[Path] = None,
                 reorientation: Optional[bool] = False,
                 deskew: Optional[bool] = False,
                 smoothing: Optional[bool] = False,
                 adaptive_binarization: Optional[bool] = True,
                 ) -> None:
        super().__init__()
        self.custom_lexicon_path = custom_lexicon_path
        self.reorientation = reorientation
        self.deskew = deskew
        self.smoothing = smoothing
        self.adaptive_binarization = adaptive_binarization

    # TODO: This function creates images that do not work wirh IDRS in some cases (error 1104)
    # @staticmethod
    # def set_resolution(image_path: Path, resolution: int):
    #     im = Image.open(image_path.name)
    #     im.save(image_path, dpi=(resolution, resolution))

    @staticmethod
    def get_resolution(img: np.ndarray) -> int:
        """For simplicity we assume that real image size is A4>.
        TODO: read real resolution from input file
        """
        shape = img.shape
        if shape[0] > shape[1]:
            resolution = round(shape[0] / 11.75)
        else:
            resolution = round(shape[1] / 11.75)
        standard_resolutions = [96, 300]
        for standard_resolution in standard_resolutions:
            if 0.95*standard_resolution <= resolution <= 1.05 * standard_resolution:
                resolution = standard_resolution
                break
        return resolution

    @mim_ocr_cfg_required
    def run_ocr_to_box(self, img: np.ndarray, *args, config: Optional[str] = None,
                       preprocessed_img_output_path: Optional[Path] = None, **kwargs) -> Box:

        # path to root idrs directory must be in LD_LIBRARY_PATH
        default_idrs_library_path = mim_ocr_cfg.ocr.ocr_backend_parameters.paths.idrs_library_path
        if "LD_LIBRARY_PATH" not in os.environ:
            os.environ["LD_LIBRARY_PATH"] = default_idrs_library_path
        elif default_idrs_library_path not in os.environ["LD_LIBRARY_PATH"].split(":"):
            os.environ["LD_LIBRARY_PATH"] = f"{os.environ['LD_LIBRARY_PATH']}:{default_idrs_library_path}"

        # prepare input temporary file
        input_tmp_file = tempfile.NamedTemporaryFile(suffix=".png")
        cv2.imwrite(input_tmp_file.name, img)

        # TODO: This part creates images that do not work wirh IDRS in some cases (error 1104)
        # resolution = self.get_resolution(img)
        # self.set_resolution(input_tmp_file, resolution)

        output_tmp_file = tempfile.NamedTemporaryFile(suffix=".json")

        # prepare ocr command options
        idrs_args = [
            mim_ocr_cfg.ocr.ocr_backend_parameters.paths.idrs_ocr_script_path,
            "-language", "17",  # 17 stands for polish
            "-input", input_tmp_file.name,
            "-output", output_tmp_file.name,
            "-licence", mim_ocr_cfg.ocr.ocr_backend_parameters.paths.idrs_licence_path,
        ]
        # if we want to save preprocessed image
        if preprocessed_img_output_path is not None:
            idrs_args += ["-output-image", str(preprocessed_img_output_path)]
        # use custom lexicon
        if self.custom_lexicon_path:
            idrs_args += ["-lexicon", self.custom_lexicon_path]
        # detect orientation and apply rotation
        if self.reorientation:
            idrs_args.append("-detect_orientation")
        # apply deskew
        if self.deskew:
            idrs_args.append("-deskew")
        # optionally apply smoothing to remove noise
        if self.smoothing:
            idrs_args.append("-smoothing")
        # apply adaptive binarization instead of threshold binarization
        if self.adaptive_binarization:
            idrs_args.append("-adaptive")

        loguru.logger.debug(f"running iRDS: {' '.join(idrs_args)}")

        # run ocr
        proc = subprocess.Popen(idrs_args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                )
        stdout, stderr = proc.communicate()
        if proc.returncode:
            raise OCRBackendException(f"iDRS Backend Exception: {stderr}")

        box = Box.from_idrs_json_path(output_tmp_file.name)
        box.children[0].additional_data['page_size'] = img.shape[:2]
        return box
