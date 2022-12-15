#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
if not 'initial_cwd' in globals():
    initial_cwd = os.getcwd()
while 'ipython' in os.getcwd():
    os.chdir("../")

from typing import Dict

import numpy as np
import pandas as pd


from PIL import Image
from pathlib import Path
from matplotlib import pyplot as plt
from IPython.core.display import HTML
import cv2

from mim_ocr.image.transformations import no_transform, reorient, deskew
from mim_ocr.backends.tesseract import TesseractBackend
from mim_ocr.visualization import visualize_ocr_result
from mim_ocr.image import open_image, write_image
from mim_ocr.utils.notebook_utils import get_directory_for_notebook_images

get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# In[2]:


samples_dir = Path('sample_data')
images_dir = get_directory_for_notebook_images(initial_cwd, makedirs=True)


# In[3]:


tesseract_backend = TesseractBackend()


# In[4]:


meta = []
for path in samples_dir.iterdir():
    if not path.is_file():
        continue
    img = open_image(path)

    metadata = {'path' : path}

    transformations = [no_transform, reorient, deskew]

    for t in transformations:

        try:
            img = t(img, path, metadata)
            box = tesseract_backend.run_ocr_to_box(img)

            for stat, value in box.calc_confidence().items():
                metadata[f'{stat}_{t.__name__}'] = value

            vis = visualize_ocr_result(original_image=img, box=box, confidence_threshold=30)
            img_path = images_dir / f'{path.name}_tranformation_{t.__name__}.jpeg'
            write_image(vis, img_path)
            # 
            #plt.imshow(vis)
            #plt.show()

            
        except Exception as e:
             print(f"Got error for {path} during tranformation {t.__name__}", e)

    meta.append(metadata)
display(pd.DataFrame.from_records(meta))

