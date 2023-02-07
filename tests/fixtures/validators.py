import os

import pytest


@pytest.fixture()
def validate_cwd():
    if __file__ != os.path.join(os.getcwd(), "tests/fixtures/validators.py"):
        raise ValueError("Test can be run only in mim_ocr directory.")
