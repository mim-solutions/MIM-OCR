import re
import sys
import os
from typing import List
from ...heuristics.feature import Feature, Occurrence

# import NER resources, if present
ner_resources_path = os.environ.get("NER_RESOURCES_PATH")
if ner_resources_path:
    if os.path.exists(ner_resources_path):
        sys.path.append(os.path.abspath(ner_resources_path))
        from mim_ocr.heuristics.pol_roberta_ner_on_device import PolRobertaNerOnDevice


class NERFeature(Feature):
    def __init__(self, device='cpu'):
        if ner_resources_path:
            if os.path.exists(ner_resources_path):
                super().__init__(name="NERFeature", priority=2)

                pretrained_model_path = os.path.join(ner_resources_path, "models", "ner_pretrained_model")
                # The model was trained as described in:
                # https://github.com/mczuk/xlm-roberta-ner#train-the-model-from-scratch

                roberta_base_model_path = os.path.join(ner_resources_path, "models", "roberta_base_fairseq")
                self.ner_model = PolRobertaNerOnDevice(pretrained_model_path, roberta_base_model_path, device=device)

            else:
                raise ValueError("Path to NER resources isn't specified correctly, check README file")
        else:
            raise ValueError("Path to NER resources isn't specified correctly, check README file")

    def find_occurrences(self, text: str) -> List[Occurrence]:
        occurrences = []

        if text.strip():  # check if input string isn't empty or whitespace
            words_and_spaces = list(filter(None, re.split(r'(\s)', text)))
            labels = [None] * len(words_and_spaces)
            words = [re.split(r'\s', text)]
            words_labels = self.ner_model.process(words)
            # process() takes a list of list of words as an argument
            # and returns a corresponding list of list of labels.
            # Each list of words constitutes a context for its elements.
            # Here, we analyze only one string at a time,
            # so process() takes a list containing one list of words as an argument,
            # and returns a list containing one list of labels.

            j = 0
            for i in range(len(words_and_spaces)):
                if not re.match(r"\s", words_and_spaces[i]):
                    labels[i] = words_labels[0][j]
                    j += 1

            word_start = 0
            for word, label in zip(words_and_spaces, labels):
                word_end = word_start + len(word)
                if label and label != "O":
                    # label "O" means that the model didn't find any relevant category for a word
                    feature_label = label + "-" + self.name
                    occurrence = Occurrence(full_text=text, feature_name=feature_label, start=word_start,
                                            end=word_end, matched_text=word, priority=self.priority)
                    occurrences.append(occurrence)
                word_start = word_end

        return occurrences
