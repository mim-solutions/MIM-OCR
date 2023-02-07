import functools
import os
from omegaconf import OmegaConf

mim_ocr_config_path = os.environ.get('MIM_OCR_CONFIG_PATH')

if mim_ocr_config_path:
    mim_ocr_cfg = OmegaConf.load(mim_ocr_config_path)
else:
    mim_ocr_cfg = None


def mim_ocr_cfg_required(func):
    """Decorator for checking that mim_ocr_cfg is present"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        check_mim_ocr_cfg_exists()
        return func(*args, **kwargs)

    return wrapper


def check_mim_ocr_cfg_exists():
    if not mim_ocr_cfg:
        raise ValueError("MIM_OCR_CONFIG_PATH environmental variable not set. You need to create a YAML config file, "
                         "and specify path in this variable. Example file can be found in "
                         "config/test_mim_ocr_conf.yaml.")
