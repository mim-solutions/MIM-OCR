import os

import torch.cuda

if os.environ.get("NER_RESOURCES_PATH"):
    from .NER_feature import NERFeature


if os.environ.get("NER_RESOURCES_PATH"):
    NER_FEATURE = NERFeature(device='cpu')

    if torch.cuda.is_available():
        NER_FEATURE_CUDA = NERFeature(device='cuda')
