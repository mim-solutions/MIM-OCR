from pathlib import Path
import loguru
import pandas as pd
from typing import List, Optional, Set, Any, Dict
import hyperscan
import re

from .feature import Feature, Occurrence
from mim_ocr.utils import isnan
from mim_ocr import mim_ocr_cfg, mim_ocr_cfg_required


class KeywordFeature(Feature):

    @mim_ocr_cfg_required
    def __init__(self, name: str, keywords: List[str], priority: int = 5,
                 allow_upper: bool = False, allow_first_letter_upper: bool = False,
                 allowed_letters_before_keyword_regex: str = "", allowed_letters_after_keyword_regex: str = "",
                 allow_recompute: bool = False):
        """
        Args:
            name:
            keywords: list of keywords that will be search in the text
            priority:
            allow_upper: if the feature is present in text if keyword is present in text in CAPITAL LETTERS.
            allow_first_letter_upper: if the feature is present in text if keyword is present with first Capital letter
            allowed_letters_before_keyword_regex: regex defining allowed text before keyword
            allowed_letters_after_keyword_regex: regex defining allowed text after keyword
            allow_recompute: Recompute hyperscan database every time. Used for automatic tests.
        """

        super().__init__(name=name, priority=priority)

        self.keywords = keywords
        self.allow_upper = allow_upper
        self.allow_first_letter_upper = allow_first_letter_upper
        self.allowed_letters_before_keyword_regex = allowed_letters_before_keyword_regex
        self.allowed_letters_after_keyword_regex = allowed_letters_after_keyword_regex
        hyperscan_db_path = Path(mim_ocr_cfg.features.keyword_features_hyperscan_databases_directory_path) / name
        if allow_recompute:
            self.compile(
                name=name, keywords=keywords,
                allow_upper=allow_upper,
                allow_first_letter_upper=allow_first_letter_upper,
                allowed_letters_before_keyword_regex=allowed_letters_before_keyword_regex,
                allowed_letters_after_keyword_regex=allowed_letters_after_keyword_regex
            )

        with open(hyperscan_db_path, 'rb') as hyperscan_db_file:
            self.hyperscan_database = hyperscan.loadb(hyperscan_db_file.read())

    @classmethod
    @mim_ocr_cfg_required
    def compile(
            cls, name: str, keywords: Set[str],
            allow_upper=False,
            allow_first_letter_upper=False,
            allowed_letters_before_keyword_regex: str = "", allowed_letters_after_keyword_regex: str = ""
    ) -> None:
        hyperscan_database = hyperscan.Database()
        loguru.logger.debug(f"Staring compilation for feature {name}")
        hyperscan_database.compile(
            expressions=[bytes(cls.compute_regex_string(
                keyword,
                allow_upper=allow_upper,
                allow_first_letter_upper=allow_first_letter_upper,
                allowed_letters_before_keyword_regex=allowed_letters_before_keyword_regex,
                allowed_letters_after_keyword_regex=allowed_letters_after_keyword_regex,
                hyperscan_compatible=True
            ), 'utf-8') for keyword in keywords],
            ids=range(len(keywords)),
            elements=len(keywords)
        )
        loguru.logger.debug(f"Finished compilation for feature {name}")
        db_path = Path(mim_ocr_cfg.features.keyword_features_hyperscan_databases_directory_path)/name
        with open(db_path, "wb") as db_file:
            db_file.write(hyperscan.dumpb(hyperscan_database))

    @classmethod
    def compute_regex_string(
        cls, keyword, allow_upper: bool = False, allow_first_letter_upper: bool = False,
        allowed_letters_before_keyword_regex: str = "", allowed_letters_after_keyword_regex: str = "",
        hyperscan_compatible: bool = False
    ) -> str:
        regex_string = rf"{re.escape(keyword)}"
        if allow_upper:
            regex_string += rf"|{re.escape(keyword.upper())}"
        if allow_first_letter_upper:
            regex_string += rf"|{re.escape(keyword[0].upper()) + re.escape(keyword[1:])}"
        keyword_inner_regex = rf"({regex_string})"
        before_regex = rf"\s|^{allowed_letters_before_keyword_regex}"
        after_regex = rf"\s|${allowed_letters_after_keyword_regex}"
        if hyperscan_compatible:
            return rf'(?:{before_regex}){keyword_inner_regex}(?:{after_regex})'
        else:
            return rf'(?:{before_regex}){keyword_inner_regex}(?={after_regex})'

    @staticmethod
    def on_match(keyword_index: int, fromm: int, to: int, flags: int,
                 context: Optional[Dict[str, Any]] = None) -> Optional[bool]:
        """See https://python-hyperscan.readthedocs.io/en/latest/usage/"""

        context['matching_ids'].add(keyword_index)
        return False

    def find_occurrences(self, text: str) -> List[Occurrence]:
        """See https://python-hyperscan.readthedocs.io/en/latest/usage/"""
        occurrences: List[Occurrence] = []
        matching_ids = set()
        self.hyperscan_database.scan(bytes(text, 'utf-8'), match_event_handler=self.on_match, context={
            'matching_ids': matching_ids,
        })
        for keyword_index in matching_ids:
            keyword = self.keywords[keyword_index]
            regex_string = self.compute_regex_string(
                keyword,
                allow_upper=self.allow_upper,
                allow_first_letter_upper=self.allow_first_letter_upper,
                allowed_letters_before_keyword_regex=self.allowed_letters_before_keyword_regex,
                allowed_letters_after_keyword_regex=self.allowed_letters_after_keyword_regex,
            )
            for m in re.finditer(regex_string, text):
                if m.groups():
                    occurrences.append(
                        Occurrence(text, self.name, m.span(1)[0], m.span(1)[1], m.group(1), self.priority))
        return occurrences


class DataFrameBasedKeywordFeature(KeywordFeature):
    def __init__(self, name: str, keywords_df: pd.DataFrame, keyword_columns: Optional[List[str]], priority: int = 5,
                 allow_upper: bool = False, allow_first_letter_upper: bool = False,
                 allowed_letters_before_keyword_regex: str = "", allowed_letters_after_keyword_regex: str = "",
                 allow_recompute: bool = False):
        keywords = keywords_df.values.tolist()
        keyword_list = [item.strip() for sublist in keywords for item in sublist if not isnan(item)]

        super().__init__(name, keyword_list, priority, allow_upper, allow_first_letter_upper,
                         allowed_letters_before_keyword_regex=allowed_letters_before_keyword_regex,
                         allowed_letters_after_keyword_regex=allowed_letters_after_keyword_regex,
                         allow_recompute=allow_recompute)


class ExcelKeywordFeature(DataFrameBasedKeywordFeature):
    def __init__(self, name: str, excel_file_path: str, keyword_columns: Optional[List[str]], priority: int = 5,
                 allow_upper: bool = False,
                 allowed_letters_before_keyword_regex: str = "", allowed_letters_after_keyword_regex: str = "",
                 allow_recompute: bool = False):
        keywords_df = pd.read_excel(excel_file_path, usecols=keyword_columns)
        super().__init__(name, keywords_df, keyword_columns, priority, allow_upper,
                         allowed_letters_before_keyword_regex=allowed_letters_before_keyword_regex,
                         allowed_letters_after_keyword_regex=allowed_letters_after_keyword_regex,
                         allow_recompute=allow_recompute)


class CSVKeywordFeature(DataFrameBasedKeywordFeature):
    def __init__(self, name: str, csv_file_path: str, keyword_columns: Optional[List[str]], priority: int = 5,
                 allow_upper: bool = False, allow_first_letter_upper: bool = False,
                 allowed_letters_before_keyword_regex: str = "", allowed_letters_after_keyword_regex: str = "",
                 allow_recompute: bool = False):
        keywords_df = pd.read_csv(csv_file_path, usecols=keyword_columns)
        super().__init__(name, keywords_df, keyword_columns, priority, allow_upper, allow_first_letter_upper,
                         allowed_letters_before_keyword_regex=allowed_letters_before_keyword_regex,
                         allowed_letters_after_keyword_regex=allowed_letters_after_keyword_regex,
                         allow_recompute=allow_recompute)
