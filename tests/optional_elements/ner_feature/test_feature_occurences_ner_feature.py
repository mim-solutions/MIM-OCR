import os
from pytest import mark
from mim_ocr.heuristics import Occurrence, find_heuristic_features

if os.environ.get("NER_RESOURCES_PATH"):
    from mim_ocr.optional_elements.ner_feature import NER_FEATURE


@mark.parametrize(
    ("text", "matches"),
    [
        ("Warszawa", [Occurrence(full_text="Warszawa", feature_name="B-nam_loc_gpe_city-NERFeature",
                                 start=0, end=8, matched_text="Warszawa", priority=2)]),
        ("Jadę na wakację do Lublina", [Occurrence(full_text="Jadę na wakację do Lublina",
                                                   feature_name="B-nam_loc_gpe_city-NERFeature",
                                                   start=19, end=26, matched_text='Lublina', priority=2)]),
        (" Piękny ;,   Wrocław  ", [Occurrence(full_text=" Piękny ;,   Wrocław  ",
                                               feature_name="B-nam_loc_gpe_city-NERFeature",
                                               start=13, end=20, matched_text='Wrocław', priority=2)]),
        ("", [])
    ]
)
def test_ner_feature_occurrences(text, matches):
    if os.environ.get("NER_RESOURCES_PATH"):
        feature_occurrences = find_heuristic_features(text, features=[NER_FEATURE])
        assert feature_occurrences == matches
