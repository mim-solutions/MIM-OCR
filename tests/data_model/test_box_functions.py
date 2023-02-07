from mim_ocr.backends import TesseractBackend
from mim_ocr.data_model.box import BoxType
from mim_ocr.data_model.box_functions import run_ocr_on_box, run_ocr_on_single_box
from mim_ocr.image import open_image

INPUT_DATA = {
    "example_tesseract_image_path": "tests/input_data/example_report1.png",
}


def test_run_ocr_on_single_box(validate_cwd):
    img = open_image(INPUT_DATA["example_tesseract_image_path"])
    backend = TesseractBackend()

    box = backend.run_ocr_to_box(img)
    b = box.children[0]

    b = run_ocr_on_single_box(backend, img, b)
    assert b.children

    b = next(b for b in box.preorder_traversal() if b.text)

    b = run_ocr_on_single_box(backend, img, b)
    assert not b.text


def test_run_ocr_on_box(validate_cwd):
    img = open_image(INPUT_DATA["example_tesseract_image_path"])

    for box_type in [BoxType.TESSERACT_PAGE, BoxType.TESSERACT_PARAGRAPH]:
        backend = TesseractBackend()
        box = backend.run_ocr_to_box(img)
        df = box.to_dataframe()
        n_boxes_type = (df['box_type'] == box_type.value).sum()

        box = run_ocr_on_box(backend, img, box, box_type=box_type)
        new_df = box.to_dataframe()
        n_new_boxes_type = (new_df['box_type'] == box_type.value).sum()

        assert n_boxes_type <= n_new_boxes_type
