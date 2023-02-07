from typing import List, Callable

from mim_ocr.backends import OCRBackend
import mim_ocr.heuristics
from mim_ocr.heuristics import Feature
from mim_ocr.image.transformations import reorient, deskew

from mim_ocr.pipeline.batch_processing import batch_run_pipeline_and_save_dataframe_for_dirs, \
    RunPipelineAndSaveDataframeInput
from mim_ocr.pipeline.batch_processing import OcrBatchProcessingArgumentParser

if __name__ == "__main__":
    parser = OcrBatchProcessingArgumentParser()

    args = parser.parse_args()

    backend = OCRBackend.get_by_name(args.backend) if args.backend is not None else None

    preprocessing_transformations: List[Callable] = []
    if args.reorient:
        preprocessing_transformations.append(reorient)
    if args.deskew:
        preprocessing_transformations.append(deskew)

    features: List[Feature] = []
    if args.features:
        for feature_name in args.features:
            feature = getattr(mim_ocr.heuristics, feature_name)
            assert isinstance(feature, Feature)
            features.append(feature)

    # To avoid using a lot of arguments we put them inside a dataclass
    pipeline_args = RunPipelineAndSaveDataframeInput(
        image_input_path=args.input_img_dir,
        out_dir=args.out_dir,
        prep_dir=args.prep_dir,
        nr_proc=args.nr_proc,
        backend=backend,
        preprocessing_transformations=preprocessing_transformations,
        input_box_path=args.input_box_dir,
        features=features,
        batch_size=args.batch_size,
    )

    batch_run_pipeline_and_save_dataframe_for_dirs(pipeline_args)
