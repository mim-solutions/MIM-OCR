from pytest import mark

from mim_ocr.heuristics import Occurrence
from mim_ocr.heuristics.fuzzy_matching_keyword_feature import pl_weighted_levenshtein, POLISH_LETTER_COST, \
    FuzzyMatchKeywordFeature


@mark.parametrize(
    ('string1', 'string2', 'expected_distance'),
    [
        ("abc", 'abc', 0.0),
        ("aęą", 'aęą', 0.0),
        ("ab c", 'ab c', 0.0),
        ("eą", 'ea', POLISH_LETTER_COST),
        ("ęą", 'ea', 2*POLISH_LETTER_COST),
        ("e", 'ε', 1.0),
        ("gg", 'ggε', 1.0),
        ("le", 'li', 0.9486),
        ("lę", 'li', 0.9486+POLISH_LETTER_COST),
    ]
)
def test_weighted_levenshtein(string1, string2, expected_distance):
    assert round(pl_weighted_levenshtein.distance(string1, string2), 4) == expected_distance


fuzzy_feature = FuzzyMatchKeywordFeature("fuzzy feature", priority=1.0,
                                         keywords=["k1", "keyword 2", "ęą keyword_3", "ea keyword_3"])


@mark.parametrize(
    ("string", 'occurrences'),
    [
        ("Ala", []),
        ("a " * 30, []),
        ("k1", [Occurrence(full_text="k1", feature_name="fuzzy feature", start=0, end=1, matched_text="k1",
                           priority=fuzzy_feature.priority, additional_info="k1")]),
        ("k1.", [Occurrence(full_text="k1.", feature_name="fuzzy feature", start=0, end=2, matched_text="k1.",
                            priority=fuzzy_feature.priority, additional_info="k1")]),
        ("k1.A", []),
        ("k1..", [Occurrence(full_text='k1..', feature_name='fuzzy feature', start=0, end=3, matched_text='k1..',
                             priority=fuzzy_feature.priority, additional_info="k1")]),
        ("k1...", []),
        ("eą kyword_3", [Occurrence(full_text='eą kyword_3', feature_name='fuzzy feature',
                                    start=0, end=10, matched_text='eą kyword_3', priority=fuzzy_feature.priority,
                                    additional_info="ęą keyword_3"),
                         Occurrence(full_text='eą kyword_3', feature_name='fuzzy feature',
                                    start=0, end=10, matched_text='eą kyword_3', priority=fuzzy_feature.priority,
                                    additional_info="ea keyword_3")]),
    ]
)
def test_fuzzy_match_keyword_feature(string, occurrences):

    assert set(fuzzy_feature.find_occurrences(string)) == set(occurrences)
