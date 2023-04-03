# EasyOCR Readme

To use EasyOCR You need to install optional requirements:

```shell
pip install  -r build/optional_requirements/easy_ocr_requirements.txt
```

Then (since this OCR backend is optional) you have to import it in a bit different way:
```python

from mim_ocr.optional_elements.easy_ocr import EasyOCRBackend

```
