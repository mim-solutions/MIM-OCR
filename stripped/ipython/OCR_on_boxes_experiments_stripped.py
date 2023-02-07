#!/usr/bin/env python
# coding: utf-8

# # Run OCR on previously identified boxes
# 
# The notebook presents a usage of the function `run_ocr_on_box`, where one can run an OCR algorithm on the boxes identifed by the same or another OCR.
# 
# Here as OCR backends Tesseract and EasyOCR are used.
# 
# One can observe that running EasyOCR after Tesseract is quite time-consuming, especially on lower levels like lines.

# In[18]:


import os
while 'ipython' in os.getcwd():
    os.chdir("../")

from typing import Dict

import numpy as np
import pandas as pd

from PIL import Image
from pathlib import Path
from matplotlib import pyplot as plt
from IPython.core.display import HTML


from mim_ocr.image.transformations import no_transform, reorient, deskew
from mim_ocr.backends.tesseract import TesseractBackend
from mim_ocr.backends.easy_ocr import EasyOCRBackend
from mim_ocr.data_model.box_functions import run_ocr_on_box
from mim_ocr.data_model.box import BoxType
from mim_ocr.visualization import visualize_ocr_result
from mim_ocr.image import open_image

get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# In[2]:


samples_dir = Path('sample_data')
plt.rcParams['figure.figsize'] = (120, 60)


# In[3]:


path = list(samples_dir.iterdir())[1]


# In[4]:


path


# In[5]:


img = open_image(path)


# ## Tesseract

# In[ ]:


tesseract_backend = TesseractBackend()


# In[7]:


get_ipython().run_cell_magic('time', '', 'box = tesseract_backend.run_ocr_to_box(img)')


# In[8]:


vis = visualize_ocr_result(original_image=img, box=box, confidence_threshold=30)
plt.imshow(vis)


# ### Tesseract after tesseract on paragraphs (level 3)
# 
# One cannot see important differences.

# In[19]:


get_ipython().run_cell_magic('time', '', 'box = run_ocr_on_box(tesseract_backend, img, box, box_type=BoxType.TESSERACT_PARAGRAPH)')


# In[20]:


vis = visualize_ocr_result(original_image=img, box=box, confidence_threshold=30)
plt.imshow(vis)


# ### Tesseract after Tesseract on lines (level 4)

# In[21]:


get_ipython().run_cell_magic('time', '', 'box = tesseract_backend.run_ocr_to_box(img)
box = run_ocr_on_box(TesseractBackend, img, box, box_type=BoxType.TESSERACT_LINE)')


# In[22]:


vis = visualize_ocr_result(original_image=img, box=box, confidence_threshold=30)
plt.imshow(vis)


# ### EasyOCR after Tesseract on paragraphs (level 3)
# 
# Some places are better (Leukocyty), but some are worse.

# In[23]:


get_ipython().run_cell_magic('time', '', 'box = tesseract_backend.run_ocr_to_box(img)
box = run_ocr_on_box(EasyOCRBackend, img, box, box_type=BoxType.TESSERACT_PARAGRAPH)')


# In[24]:


vis = visualize_ocr_result(original_image=img, box=box, confidence_threshold=30)
plt.imshow(vis)


# ### EasyOCR after Tesseract on lines (level 4)
# 
# Some places are better (Leukocyty), but some are worse.

# In[25]:


get_ipython().run_cell_magic('time', '', 'box = tesseract_backend.run_ocr_to_box(img)
box = run_ocr_on_box(EasyOCRBackend, img, box, box_type=BoxType.TESSERACT_LINE)')


# In[26]:


vis = visualize_ocr_result(original_image=img, box=box, confidence_threshold=30)
plt.imshow(vis)


# ### EasyOCR

# In[ ]:


easy_ocr_backend = EasyOCRBackend()


# In[28]:


get_ipython().run_cell_magic('time', '', 'box = easy_ocr_backend.run_ocr_to_box(img)')


# In[29]:


vis = visualize_ocr_result(original_image=img, box=box, confidence_threshold=30)
plt.imshow(vis)


# ### Tesseract after EasyOCR
# 
# The worst performance.

# In[30]:


get_ipython().run_cell_magic('time', '', 'box = run_ocr_on_box(TesseractBackend, img, box)')


# In[31]:


vis = visualize_ocr_result(original_image=img, box=box, confidence_threshold=30)
plt.imshow(vis)

