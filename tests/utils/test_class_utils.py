from pytest import raises

from mim_ocr.utils.class_utils import get_subclass_by_name


def test_get_subclass_by_name_correct(validate_cwd):
    assert get_subclass_by_name(Exception, "Exception") == Exception
    assert get_subclass_by_name(BaseException, "BrokenPipeError") == BrokenPipeError
    assert get_subclass_by_name(BaseException, "Exception") == Exception


def test_get_subclass_by_name_raise(validate_cwd):
    with raises(KeyError):
        get_subclass_by_name(ArithmeticError, "ImportError")
