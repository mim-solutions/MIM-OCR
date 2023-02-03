import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

# Dictionary mapping features names to their priority.
# The box read from a file may already have some features' occurrences recognized.
# When computing some other features on such box, we use this dictionary to check,
# if the feature occurrence found now for a given word, should overwrite feature occurrence found previously.
FEATURES_PRIORITIES_DICTIONARY = {"Number": 5, "PhoneNumber": 7, "Date": 8, "PESEL": 10}

if os.environ.get("NER_RESOURCES_PATH"):
    FEATURES_PRIORITIES_DICTIONARY["NERFeature"] = 2


@dataclass(eq=True, frozen=True)
class Occurrence:
    full_text: str
    feature_name: str
    start: int
    end: int
    matched_text: str
    priority: int
    additional_info: Optional[str] = None

    @staticmethod
    def get_occurrences_from_regex(regex: re.Pattern, text: str, feature_name: str, feature_priority: int) \
            -> List['Occurrence']:

        occurrences: List[Occurrence] = []
        for m in re.finditer(regex, text):
            if m.groups():
                occurrences.append(
                    Occurrence(text, feature_name, m.span(1)[0], m.span(1)[1], m.group(1), feature_priority))
        return occurrences


class Feature(ABC):

    def __init__(self, name: str, priority: int = 5):
        """
        Args:
            name: name of the feature
            priority:  priority will be used when two features overlap and one of features needs to be
                       chosen or presented.
                       higher number (like 9) means detailed features (like PESEL).
                       lower number (like 0) means general features (like Number).
        """

        self.name = name
        self.priority = priority

    @abstractmethod
    def find_occurrences(self, text: str) -> List[Occurrence]:
        pass

    @classmethod
    def get_feature_priority_by_name(cls, name: str) -> int:

        # remove "<-", "-" and "->" suffixes
        name = name.rstrip("<->")

        if name in FEATURES_PRIORITIES_DICTIONARY:
            return FEATURES_PRIORITIES_DICTIONARY[name]

        # NERFeature occurrences have different names, depending on the category recognized by NER,
        # but everytime it has "NERFeature" suffix.
        elif name.endswith("NERFeature"):
            return FEATURES_PRIORITIES_DICTIONARY["NERFeature"]

        raise ValueError(f"Cannot determine priority for {name} feature occurrence.")
