import re
from typing import List

from .feature import Feature, Occurrence


class RegexFeature(Feature):
    def __init__(self, name: str, core_regex: str, before_regex: str = "", after_regex: str = "", priority: int = 5):
        """
        Args:
            name:
            core_regex: regex that will be matched in feature occurrence
            before_regex: regex that needs to match text before feature occurrence
            after_regex: regex that needs to match text after feature occurrence
            priority:
        """

        super().__init__(name, priority=priority)
        self.regex = re.compile(rf'(?:{before_regex})({core_regex})(?={after_regex})')
        # "({core_regex})(?={after_regex})" means, that pattern of core_regex
        # has to be followed by pattern of after_regex, to be matched,
        # but after_regex pattern is not included in the match

    def find_occurrences(self, text: str) -> List[Occurrence]:
        return Occurrence.get_occurrences_from_regex(self.regex, text, self.name, self.priority)
