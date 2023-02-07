import json
from typing import List
import numpy as np
import pandas as pd
from strsimpy.weighted_levenshtein import WeightedLevenshtein
from symspellpy import SymSpell, Verbosity

from mim_ocr import mim_ocr_cfg, check_mim_ocr_cfg_exists
from mim_ocr.heuristics import Feature, Occurrence
from mim_ocr.utils import isnan


POLISH_LETTER_COST = 0.1
POLISH_LETTERS_LINKS = {
    'Ą': 'A',
    'ą': 'a',
    'Ę': 'E',
    'ę': 'e',
    'Ł': 'L',
    'ł': 'l',
    'Ć': 'C',
    'ć': 'c',
    'Ń': 'N',
    'ń': 'n',
    'Ó': 'O',
    'ó': 'o',
    'Ś': 'S',
    'ś': 's',
    'Ź': 'Z',
    'ź': 'z',
    'Ż': 'Z',
    'ż': 'z',
}
# Maximum difference between keyword length and matched test lenghts (use for speedup)
# Higher value will allow more fuzzy results: e.g. with more additional dots
ALLOWED_WORD_LEN_DIFFERENCE: int = 2

# Length of the string at which distance 1.0 should be accepted
MAXIMUM_DISTANCE_LENGTH_WITH_COEFFICIENT_1 = 4.0

# Power which used to scale the allowed distance.
# MAXIMUM_DISTANCE_POWER = 0.5 means that if you make string 4 times longer
# the allowed distance will double
MAXIMUM_DISTANCE_POWER = 0.5

# Maximum ord() of precalculated weighted distance matrix.
LEVEN_PARAMS_SIZE = 128

# Maximum number of words allowed in text
MAX_WORD_NUMBER = 20

SYMSPELL_PREFIX_LENGTH = 7 # noqa see https://towardsdatascience.com/symspell-vs-bk-tree-100x-faster-fuzzy-string-search-spell-checking-c4f10d80a078 fro explanation
SYMSPELL_MAX_DISTANCE = 3
SYMSEPELL_MAX_LEN_DISTANCE_1 = 3
SYMSEPELL_MAX_LEN_DISTANCE_2 = 6


check_mim_ocr_cfg_exists()
with open(mim_ocr_cfg.features.fuzzy_matching.params_weighted_leven_path, "r") as f:
    leven_params = json.load(f)
    for k in leven_params.keys():
        if k == "comment":
            continue
        assert len(leven_params[k]) == LEVEN_PARAMS_SIZE
        leven_params[k] = np.array(leven_params[k])


def get_single_operation_cost(key: str, char: str):
    if key not in ('insert_costs', 'delete_costs'):
        raise ValueError("Incorrect key.")
    if len(char) > 1:
        raise ValueError("Only single char accepted.")
    o = ord(char)
    if o < LEVEN_PARAMS_SIZE:
        return leven_params[key][o]
    if char in POLISH_LETTERS_LINKS:
        return leven_params[key][ord(POLISH_LETTERS_LINKS[char])]+POLISH_LETTER_COST
    return 1.0


def get_insertion_cost(char: str):
    return get_single_operation_cost('insert_costs', char)


def get_deletion_cost(char: str):
    return get_single_operation_cost('delete_costs', char)


def get_substitution_cost(char_a: str, char_b: str):
    o_a = ord(char_a)
    o_b = ord(char_b)
    if o_a < LEVEN_PARAMS_SIZE and o_b < LEVEN_PARAMS_SIZE:
        return leven_params['substitute_costs'][o_a][o_b]
    if char_a in POLISH_LETTERS_LINKS:
        if char_b == POLISH_LETTERS_LINKS[char_a]:
            return POLISH_LETTER_COST
        return get_substitution_cost(POLISH_LETTERS_LINKS[char_a], char_b) + POLISH_LETTER_COST
    if char_b in POLISH_LETTERS_LINKS:
        if char_a == POLISH_LETTERS_LINKS[char_b]:
            return POLISH_LETTER_COST
        return get_substitution_cost(char_a, POLISH_LETTERS_LINKS[char_b]) + POLISH_LETTER_COST
    return 1.0


pl_weighted_levenshtein = WeightedLevenshtein(
    substitution_cost_fn=get_substitution_cost,
    insertion_cost_fn=get_insertion_cost,
    deletion_cost_fn=get_deletion_cost)


class FuzzyMatchKeywordFeature(Feature):
    """
    Feature that looks for keywords using weighted-levenshtein algorithm.
    Weight are taken from https://github.com/zas97/ocr_weighted_levenshtein

    Good description on how does weighted levenshtein algorithm works can be found on
    https://github.com/infoscout/weighted-levenshtein
    """
    def __init__(self, name: str, keywords: List[str], priority: int = 5,
                 allow_upper: bool = False):

        super().__init__(name, priority=priority)

        if allow_upper:
            keywords = list(set(keywords+[keyword.upper() for keyword in keywords]))
        keywords.sort()

        self.sym_spell = SymSpell(max_dictionary_edit_distance=SYMSPELL_MAX_DISTANCE,
                                  prefix_length=SYMSPELL_PREFIX_LENGTH)

        for keyword in keywords:
            self.sym_spell.create_dictionary_entry(keyword, 1)

        self.keywords_by_words_count_and_length: dict[int, dict[int, [List[str]]]] = \
            {i: {} for i in range(MAX_WORD_NUMBER)}

        for keyword in keywords:
            nr_words = len(keyword.split(" "))
            keyword_len = len(keyword)
            self.keywords_by_words_count_and_length[nr_words].setdefault(keyword_len, []).append(keyword)

    def find_occurrences(self, text: str) -> List[Occurrence]:
        if "  " in text:
            raise ValueError("Multiple spaces are not supported.")

        occurrences: List[Occurrence] = []

        words = text.split(" ")
        nr_words = len(words)
        for word_frame_length in range(1, MAX_WORD_NUMBER+1):
            current_start_position = 0
            for i in range(nr_words-word_frame_length+1):
                t = " ".join(words[i:i + word_frame_length])
                occurrences += self.\
                    find_occurrences_for_word_frame_and_position(search_text=t,
                                                                 word_frame_length=word_frame_length,
                                                                 current_start_position=current_start_position,
                                                                 full_text=text)
                current_start_position += len(words[i])+1
        return occurrences

    def find_occurrences_for_word_frame_and_position(self, search_text: str, word_frame_length: int,
                                                     current_start_position: int,
                                                     full_text: str) -> List[Occurrence]:
        """Distance between search text and keywords is calculated using weighted Levenstein algorithm.
        Maximum allowed distance is proportional to MAXIMUM_DISTANCE_POWER of the search word length.

        Fuzzy mathing is not allowed for strings of length 1.
        """

        occurrences: List[Occurrence] = []

        if len(search_text) <= SYMSEPELL_MAX_LEN_DISTANCE_1:
            max_symspell_distance = 1
        elif len(search_text) <= SYMSEPELL_MAX_LEN_DISTANCE_2:
            max_symspell_distance = 2
        else:
            max_symspell_distance = 3

        if not self.sym_spell.lookup(search_text, Verbosity.CLOSEST, max_edit_distance=max_symspell_distance):
            return occurrences

        t_length = len(search_text)
        current_end_position = current_start_position + t_length - 1
        for j in range(max(1, t_length - ALLOWED_WORD_LEN_DIFFERENCE), t_length + ALLOWED_WORD_LEN_DIFFERENCE):
            for keyword in self.keywords_by_words_count_and_length.get(word_frame_length, {}).get(j, []):
                distance = pl_weighted_levenshtein.distance(search_text, keyword)
                if distance == 0 or (((distance * MAXIMUM_DISTANCE_LENGTH_WITH_COEFFICIENT_1 / t_length)
                                      ** MAXIMUM_DISTANCE_POWER <= 1) and t_length > 1):
                    occurrences.append(Occurrence(full_text=full_text, feature_name=self.name,
                                                  start=current_start_position, end=current_end_position,
                                                  matched_text=search_text, priority=self.priority,
                                                  additional_info=keyword))
        return occurrences


class CSVFuzzyMatchKeywordFeature(FuzzyMatchKeywordFeature):
    """Any CSV format that can be read by Pandas is supported.
    every cell in the first sheet (except for the header) are treated as keywords."""
    def __init__(self, name: str, csv_path: str, priority: int = 5,
                 allow_upper: bool = False):
        keywords_df = pd.read_csv(csv_path)
        keywords = keywords_df.values.tolist()
        keyword_list = [item.strip() for sublist in keywords for item in sublist if not isnan(item)]

        super().__init__(name, priority=priority, keywords=keyword_list, allow_upper=allow_upper)
