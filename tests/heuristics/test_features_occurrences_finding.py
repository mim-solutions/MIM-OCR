from pytest import mark

from mim_ocr.heuristics import NUMBER_FEATURE, PHONE_NUMBER_FEATURE, DATE_FEATURE, PESEL_FEATURE, \
                               KeywordFeature
from mim_ocr.heuristics import find_heuristic_features, Occurrence
from mim_ocr.heuristics.extract_simple_results import TextLineAnalysis


@mark.parametrize(
    ("text", "matches"),
    [
        ("123",
         [Occurrence(full_text='123', feature_name="Number", start=0, end=3, matched_text='123', priority=5)]),
        (
                "12.3",
                [Occurrence(full_text='12.3', feature_name="Number", start=0, end=4, matched_text='12.3', priority=5)]),
        (
                "12,3",
                [Occurrence(full_text='12,3', feature_name="Number", start=0, end=4, matched_text='12,3', priority=5)]),
        ("123 ", [Occurrence(full_text='123 ', feature_name="Number", start=0, end=3, matched_text='123', priority=5)]),
        (" 123", [Occurrence(full_text=' 123', feature_name="Number", start=1, end=4, matched_text='123', priority=5)]),
        ("x 123",
         [Occurrence(full_text='x 123', feature_name="Number", start=2, end=5, matched_text='123', priority=5)]),
        ("123-", []),
        (
                ">123",
                [Occurrence(full_text='>123', feature_name="Number", start=0, end=4, matched_text='>123', priority=5)]),
        ('5.123', [Occurrence(full_text='5.123', feature_name="Number", start=0, end=5, matched_text='5.123',
                              priority=5)]),
        ('5,123', [Occurrence(full_text='5,123', feature_name="Number", start=0, end=5, matched_text='5,123',
                              priority=5)]),
        ("123 22 30 90 3456", [Occurrence(full_text='123 22 30 90 3456', feature_name="Number", start=0, end=3,
                                          matched_text="123", priority=5),
                               Occurrence(full_text='123 22 30 90 3456', feature_name="Number", start=4, end=6,
                                          matched_text='22', priority=5),
                               Occurrence(full_text='123 22 30 90 3456', feature_name="Number", start=7, end=9,
                                          matched_text='30', priority=5),
                               Occurrence(full_text='123 22 30 90 3456', feature_name="Number", start=10, end=12,
                                          matched_text='90', priority=5),
                               Occurrence(full_text='123 22 30 90 3456', feature_name="Number", start=13, end=17,
                                          matched_text='3456', priority=5),
                               ])
    ]
)
def test_number_feature(text, matches):
    feature_occurrences = find_heuristic_features(text, features=[NUMBER_FEATURE])
    assert set(feature_occurrences) == set(matches)


@mark.parametrize(
    ("text", "matches"),
    [
        ("782011188", [Occurrence(full_text="782011188", feature_name="PhoneNumber", start=0, end=9,
                                  matched_text='782011188', priority=7)]),
        ("782-011-188", [Occurrence(full_text="782-011-188", feature_name="PhoneNumber", start=0, end=11,
                                    matched_text='782-011-188', priority=7)]),
        ("782 011 188", [Occurrence(full_text="782 011 188", feature_name="PhoneNumber", start=0, end=11,
                                    matched_text='782 011 188', priority=7)]),
        ("TEL 782 011 188", [Occurrence(full_text="TEL 782 011 188", feature_name="PhoneNumber", start=4, end=15,
                                        matched_text='782 011 188', priority=7)]),
        ("TEL:782 011 188", [Occurrence(full_text="TEL:782 011 188", feature_name="PhoneNumber", start=4, end=15,
                                        matched_text='782 011 188', priority=7)]),
        ("123-782-011-188", []),
        ("782 011 1888", []),
        ("782 011 188 PESEL", [Occurrence(full_text="782 011 188 PESEL", feature_name="PhoneNumber", start=0, end=11,
                                          matched_text='782 011 188', priority=7)]),
        ("(56)1234567", [Occurrence(full_text="(56)1234567", feature_name="PhoneNumber", start=0, end=11,
                                    matched_text='(56)1234567', priority=7)]),
        ("56 1234567", [Occurrence(full_text="56 1234567", feature_name="PhoneNumber", start=0, end=10,
                                   matched_text='56 1234567', priority=7)]),

    ]
)
def test_phone_number_feature(text, matches):
    feature_occurrences = find_heuristic_features(text, features=[PHONE_NUMBER_FEATURE])
    assert feature_occurrences == matches


TEST_KEYWORD_FEATURE = KeywordFeature(name="TestKeyword1", keywords=["do"], allow_recompute=True)
TEST_KEYWORD_FEATURE_ALLOW_UPPER = KeywordFeature(name="TestKeyword2", keywords=["do"],
                                                  allow_upper=True, allow_recompute=True)
TEST_KEYWORD_FEATURE_ALLOWED_BEFORE_AFTER = KeywordFeature(name="TestKeyword3", keywords=["do"],
                                                           allowed_letters_before_keyword_regex="|X|Y",
                                                           allowed_letters_after_keyword_regex="|X|Y",
                                                           allow_recompute=True)


@mark.parametrize(
    ("text", "features", "matches"),
    [
        ("2 do 3", [TEST_KEYWORD_FEATURE], [Occurrence(full_text="2 do 3", feature_name="TestKeyword1", start=2, end=4,
                                                       matched_text='do', priority=5)]),
        ("2 DO 3", [TEST_KEYWORD_FEATURE], []),
        ("2 DO 3", [TEST_KEYWORD_FEATURE_ALLOW_UPPER],
         [Occurrence(full_text="2 DO 3", feature_name="TestKeyword2", start=2, end=4, matched_text='DO', priority=5)]),
        ("2 do 3", [TEST_KEYWORD_FEATURE_ALLOW_UPPER],
         [Occurrence(full_text="2 do 3", feature_name="TestKeyword2", start=2, end=4,
                     matched_text='do', priority=5)]),
        ("2Xdo 3", [TEST_KEYWORD_FEATURE], []),
        ("2 doY3", [TEST_KEYWORD_FEATURE], []),
        ("2Xdo 3", [TEST_KEYWORD_FEATURE_ALLOWED_BEFORE_AFTER],
         [Occurrence(full_text="2Xdo 3", feature_name="TestKeyword3", start=2, end=4,
                     matched_text='do', priority=5)]),
        ("2 doY3", [TEST_KEYWORD_FEATURE_ALLOWED_BEFORE_AFTER],
         [Occurrence(full_text="2 doY3", feature_name="TestKeyword3", start=2, end=4,
                     matched_text='do', priority=5)]),
        ("do do", [TEST_KEYWORD_FEATURE],
         [Occurrence(full_text="do do", feature_name="TestKeyword1", start=0, end=2,
                     matched_text='do', priority=5),
          Occurrence(full_text="do do", feature_name="TestKeyword1", start=3, end=5,
                     matched_text='do', priority=5)
          ]),
    ]
)
def test_dummy_keyword_feature(text, features, matches):
    feature_occurrences = find_heuristic_features(text, features=features)
    assert feature_occurrences == matches


@mark.parametrize(
    ("text", "matches"),
    [
        ("2022-05-19", [Occurrence(full_text="2022-05-19", feature_name="Date", priority=DATE_FEATURE.priority,
                                   start=0, end=10, matched_text="2022-05-19")]),
        (" 1950-04-12 ", [Occurrence(full_text=" 1950-04-12 ", feature_name="Date", priority=DATE_FEATURE.priority,
                                     start=1, end=11, matched_text="1950-04-12")]),
        (" 01-11-2012 ", [Occurrence(full_text=" 01-11-2012 ", feature_name="Date", priority=DATE_FEATURE.priority,
                                     start=1, end=11, matched_text="01-11-2012")]),
        (" 05-10-2010", [Occurrence(full_text=" 05-10-2010", feature_name="Date", priority=DATE_FEATURE.priority,
                                    start=1, end=11, matched_text="05-10-2010")]),
        (":13-07-1970 05-10-2010", [Occurrence(full_text=":13-07-1970 05-10-2010", feature_name="Date",
                                               priority=DATE_FEATURE.priority, start=1, end=11,
                                               matched_text="13-07-1970"),
                                    Occurrence(full_text=":13-07-1970 05-10-2010", feature_name="Date",
                                               priority=DATE_FEATURE.priority, start=12, end=22,
                                               matched_text="05-10-2010")]),
        ("31.02.1977", [Occurrence(full_text="31.02.1977", feature_name="Date", priority=DATE_FEATURE.priority,
                                   start=0, end=10, matched_text="31.02.1977")]),
        ("13/12/2004,", [Occurrence(full_text="13/12/2004,", feature_name="Date", priority=DATE_FEATURE.priority,
                                    start=0, end=10, matched_text="13/12/2004")]),
        ("112/12/1998", []),
        ("12-05-19988", []),
        ("32-12-1998", []),
        ("12-17-1998", []),
        ("12-12-1800", [])
    ]
)
def test_date_feature(text, matches):
    feature_occurrences = TextLineAnalysis(text, features=[DATE_FEATURE]).feature_occurrences
    assert set(feature_occurrences) == set(matches)


# sample PESEL numbers generated with pesel.cstudios.pl/o-generatorze/generator-on-line
@mark.parametrize(
    ("text", "matches"),
    [
        ('87121551648',
         [Occurrence(full_text='87121551648', feature_name="PESEL", priority=PESEL_FEATURE.priority, start=0, end=11,
                     matched_text='87121551648')]),
        ('    51052654198 abcd123',
         [Occurrence(full_text='    51052654198 abcd123', feature_name="PESEL", priority=PESEL_FEATURE.priority,
                     start=4, end=15, matched_text='51052654198')]),
    ]
)
def test_PESEL_feature(text, matches):
    feature_occurrences = TextLineAnalysis(text, features=[PESEL_FEATURE]).feature_occurrences
    assert feature_occurrences == matches
