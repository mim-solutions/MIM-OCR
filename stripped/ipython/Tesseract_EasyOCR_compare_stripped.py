#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
while 'ipython' in os.getcwd():
    os.chdir("../")

from typing import Dict
import cv2
import numpy as np
import pandas as pd

from PIL import Image
from pathlib import Path
from matplotlib import pyplot as plt
from IPython.core.display import HTML

from mim_ocr.backends.tesseract import TesseractBackend
from mim_ocr.backends.easy_ocr import EasyOCRBackend
from mim_ocr.image.transformations import no_transform, reorient, deskew
from mim_ocr.visualization import visualize_ocr_result, compare_ocr_results
from mim_ocr.image import open_image

get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# ### sample images OCR results
# 
# On following images: on right we present found texts by Tesseract, on left Easy OCR.

# In[3]:


samples_dir = Path('sample_data')
plt.rcParams['figure.figsize'] = (120, 60)


# In[ ]:


display(HTML("<style>.container { width:100% !important; }</style>"))


# ### sample images OCR results
# 
# On following images: on right we present found texts, on left image (tranformed). Transformations are applied one after another.

# In[ ]:


tesseract_backend = TesseractBackend()
easy_ocr_backend = EasyOCRBackend()


# In[ ]:


meta = []
for path in samples_dir.iterdir():
    if not path.is_file():
        continue
    display(HTML(f'<h3> {path} </h3>'))
    img = open_image(path)

    metadata = {'path' : path}

    transformations = [deskew]
    
    for t in transformations:
        display(HTML(f'<h5> {t.__name__} </h5>'))
        
        try:
            img = t(img, path, metadata)
            box_tes = tesseract_backend.run_ocr_to_box(img)
            box_easy = easy_ocr_backend.run_ocr_to_box(img)

            for box, name in [(box_tes, 'tesseract'), (box_easy, 'easyocr')]:
                for stat, value in box.calc_confidence().items():
                    metadata[f'{stat}_{t.__name__}_{name}'] = value

            vis = compare_ocr_results(img, box_tes, box_easy,
                                      confidence_threshold1=30.0, confidence_threshold2=30.0)
            plt.imshow(vis)
            plt.show()
        except Exception as e:
             print(f"Got error for {path} during tranformation {t.__name__}", e)
            
    meta.append(metadata)
display(pd.DataFrame.from_records(meta))

