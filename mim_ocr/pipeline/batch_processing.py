import argparse
import dataclasses
import multiprocessing
import os
from contextlib import closing
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from pathlib import Path
from typing import Optional, List, Callable

from loguru import logger
from tqdm import tqdm

from mim_ocr.backends import OCRBackend
from mim_ocr.heuristics import Feature
from mim_ocr.pipeline.pipeline import run_pipeline_and_save_results_to_file, RunPipelineAndSaveResultToFileInput


@dataclasses.dataclass
class RunPipelineAndSaveDataframeInput:
    image_input_path: str
    out_dir: Optional[str]
    prep_dir: Optional[str]
    nr_proc: int
    backend: Optional[OCRBackend]
    input_box_path: Optional[str]
    preprocessing_transformations: List[Callable] = dataclasses.field(default_factory=lambda: [])
    features: List[Feature] = dataclasses.field(default_factory=lambda: [])

    input_img_filepaths: List[Optional[Path]] = dataclasses.field(default_factory=lambda: [])
    input_box_filepaths: List[Optional[Path]] = dataclasses.field(default_factory=lambda: [])
    preprocessed_image_paths: List[Optional[Path]] = dataclasses.field(default_factory=lambda: [])
    output_filepaths: List[Optional[Path]] = dataclasses.field(default_factory=lambda: [])

    batch_size: int = 1

    def validate(self):
        if self.image_input_path:
            if not os.path.isdir(self.image_input_path):
                raise ValueError("input_img_dir is not a valid directory path.")

            if self.out_dir is not None and not os.path.isdir(self.out_dir):
                raise ValueError("out_dir is not a valid directory path.")

            if self.prep_dir is not None and not os.path.isdir(self.prep_dir):
                raise ValueError("prep_dir is not a valid directory path.")

        if self.input_box_path:
            if not os.path.isdir(self.input_box_path):
                raise ValueError("input_img_dir is not a valid directory path.")

    def calculate_path_lists(self) -> None:
        if self.image_input_path:
            filenames = [f for f in os.listdir(self.image_input_path) if
                         os.path.isfile(os.path.join(self.image_input_path, f))]
            input_filepaths = [Path(os.path.join(self.image_input_path, f)) for f in filenames]
            self.input_img_filepaths = input_filepaths
            self.input_box_filepaths = [None for _ in input_filepaths]

        elif self.input_box_path:
            filenames = [f for f in os.listdir(self.input_box_path) if
                         os.path.isfile(os.path.join(self.input_box_path, f))]
            input_filepaths = [Path(os.path.join(self.input_box_path, f)) for f in filenames]
            self.input_box_filepaths = input_filepaths
            self.input_img_filepaths = [None for _ in input_filepaths]

        if self.out_dir is None:
            self.output_filepaths = [None for _ in input_filepaths]
        else:
            self.output_filepaths = [Path(self.out_dir, f + ".json") for f in filenames]

        if self.prep_dir is None:
            self.preprocessed_image_paths = [None for _ in input_filepaths]
        else:
            self.preprocessed_image_paths = [Path(self.out_dir, f) for f in filenames]

    def get_single_pipeline_input(self, i: int, j: int) -> List[RunPipelineAndSaveResultToFileInput]:
        return [RunPipelineAndSaveResultToFileInput(
            output_path=self.output_filepaths[k],
            image_input_path=self.input_img_filepaths[k],
            preprocessing_transformations=self.preprocessing_transformations,
            preprocessed_image_path=self.preprocessed_image_paths[k],
            backend=self.backend,
            box_input_path=self.input_box_filepaths[k],
            features=self.features,
        ) for k in range(i, j)]


def batch_run_pipeline_and_save_dataframe_for_dirs(args: RunPipelineAndSaveDataframeInput) -> None:
    """Run pipeline for all files in input directory on multiple processors.
    Save result datasheets into output directory."""

    args.validate()
    args.calculate_path_lists()

    logger.info(f"Running pipeline on {len(args.input_img_filepaths)} images.")

    if args.nr_proc == 1:
        # some elements of the pipeline, like NER_FEATURE do not run in multiprocessing environement.
        # Disabling multiprocessing for 1 CPU enables to run them.
        for i, _ in enumerate(tqdm(args.input_img_filepaths)):
            pipeline_input = args.get_single_pipeline_input(i, i+1)
            options_dict = {
                'job_info': f"filepath: {pipeline_input[0].image_input_path or pipeline_input[0].box_input_path} "
                            f"({args.batch_size} files)",
                'suppress_exceptions': True,
            }
            run_pipeline_and_save_results_to_file(pipeline_input, **options_dict)

    else:
        with closing(Pool(args.nr_proc)) as pool:
            funclist: List[ApplyResult] = []
            i = 0
            j = min(i + args.batch_size, len(args.input_img_filepaths))
            while i < j:
                pipeline_input = args.get_single_pipeline_input(i, j)
                options_dict = {
                    'job_info': f"filepath: {pipeline_input[0].image_input_path or pipeline_input[0].box_input_path} "
                                f"({args.batch_size} files)",
                    'suppress_exceptions': True,
                }

                f = pool.apply_async(run_pipeline_and_save_results_to_file,
                                     (pipeline_input,),
                                     options_dict)
                funclist.append(f)
                i = j
                j = min(i + args.batch_size, len(args.input_img_filepaths))

            for k, f in enumerate(tqdm(funclist)):
                try:
                    f.get(timeout=10000*args.batch_size)
                except multiprocessing.context.TimeoutError:
                    logger.error(
                        f"Mutiprocessing timeout error "
                        f"on input "
                        f"{args.input_img_filepaths[args.batch_size] or args.input_box_filepaths[args.batch_size]} "
                        f"({args.batch_size} files).")


class OcrBatchProcessingArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(description='batch run OCR pipeline ans save results do dataframes')

        self.add_argument('--input_img_dir', type=str, help='Directory with input images.')
        self.add_argument('--input_box_dir', type=str, help='Directory with input images.')
        self.add_argument('--out_dir', type=str, help='Directory to store output datasheets.', default=None)
        self.add_argument('--prep_dir', type=str, help='Directory to store preprocessed images.', default=None)
        self.add_argument('--nr_proc', type=int, help='number of processors to use.', default=1)
        self.add_argument('--logfile', type=Path, help='path to logfile')
        self.add_argument('--backend', type=str, help='Backend name, e.g TesseractBacked, EasyOCRBackend',
                          default=None)
        self.add_argument('--batch_size', type=int, help='Number of files processed with one worker')
        self.add_argument('--reorient', action=argparse.BooleanOptionalAction)
        self.add_argument('--deskew', action=argparse.BooleanOptionalAction)
        self.add_argument('--features', nargs='+', help='List of features to find')

    def parse_args(self, *args, **kwargs):
        parser_args = super().parse_args(*args, **kwargs)

        if parser_args.logfile:
            logger.remove()
            logger.add(parser_args.logfile, mode="w")

        if parser_args.out_dir and not (parser_args.backend or parser_args.input_box_dir):
            raise ValueError("You need to provide backend together with out_ocr_dir.")

        if not (parser_args.out_dir or parser_args.prep_dir):
            raise ValueError("Nothing to do, no output dirs provided.")

        return parser_args
