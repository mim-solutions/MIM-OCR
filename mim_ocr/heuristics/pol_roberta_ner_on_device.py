import os
import sys
import torch
from loguru import logger

# import NER resources, if present
ner_resources_path = os.environ.get("NER_RESOURCES_PATH")
if ner_resources_path:
    if os.path.exists(ner_resources_path):
        sys.path.append(os.path.abspath(ner_resources_path))
        from core.polrobertner import PolRobertaNer
        from core.model.xlmr_for_token_classification import XLMRForTokenClassification


class PolRobertaNerOnDevice(PolRobertaNer):
    # this class is based on PolRobertaNer, but allows to specify whether the computations should be done on cpu or cuda

    def __init__(self, model_path: str, roberta_embeddings_path: str, device: str = None):
        # code of this constructor was copied from the parent class PolRobertaNer
        # and modified, to allow specifying the device on which, the model is run ("cpu" or "cuda")
        if not os.path.exists(model_path):
            raise ValueError("Model not found on path '%s'" % model_path)

        if not os.path.exists(roberta_embeddings_path):
            raise ValueError("RoBERTa language model not found on path '%s'" % roberta_embeddings_path)

        if not device:
            if torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
        logger.info(f'NER computations using {device} device')

        self.label_list = PolRobertaNer.load_labels(os.path.join(model_path, 'labels.txt'))
        model = XLMRForTokenClassification(pretrained_path=roberta_embeddings_path,
                                           n_labels=len(self.label_list) + 1,
                                           hidden_size=768 if 'base' in roberta_embeddings_path else 1024,
                                           device=device)
        with open(os.path.join(model_path, 'model.pt'), 'rb') as model_file:
            state_dict = torch.load(model_file, map_location=torch.device(device))
        model.load_state_dict(state_dict)
        model.eval()
        self.model = model
