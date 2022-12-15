from mim_ocr import mim_ocr_cfg, mim_ocr_cfg_required
from mim_ocr.data_model import IDRSWordAdditionalData, IDRSTextElement, IDRSTextElementAlternative


def test_get_text_alternatives_no_alternatives():
    word_additional_data = IDRSWordAdditionalData([
        IDRSTextElement(text="x", confidence=0),
        IDRSTextElement(text="y", confidence=1),
    ])

    text_alternatives = word_additional_data.get_text_alternatives()
    assert text_alternatives == [("xy", 0, [-1, -1])]


def test_get_text_alternatives_no_max_confidence():
    word_additional_data = IDRSWordAdditionalData([
        IDRSTextElement(text="x", confidence=0),
        IDRSTextElement(text="y", confidence=1, alternatives=[
            IDRSTextElementAlternative(text="z", confidence=2),
        ])
    ])

    text_alternatives = word_additional_data.get_text_alternatives()
    assert text_alternatives == [("xy", 0, [-1, -1]), ("xz", 1, [-1, 0])]


def test_get_text_alternatives_max_confidence():
    word_additional_data = IDRSWordAdditionalData([
        IDRSTextElement(text="x", confidence=0),
        IDRSTextElement(text="y", confidence=1, alternatives=[
            IDRSTextElementAlternative(text="z", confidence=2),
        ])
    ])

    text_alternatives = word_additional_data.get_text_alternatives(max_confidence_loss=0)
    assert text_alternatives == [("xy", 0, [-1, -1])]


@mim_ocr_cfg_required
def test_max_nr_of_alternatives():
    word_additional_data = IDRSWordAdditionalData([
        IDRSTextElement(text="a1", confidence=0, alternatives=[
            IDRSTextElementAlternative(text="a2", confidence=2),
            IDRSTextElementAlternative(text="a3", confidence=2),
            IDRSTextElementAlternative(text="a4", confidence=2),
            IDRSTextElementAlternative(text="a5", confidence=2),
        ]),
        IDRSTextElement(text="b1", confidence=0, alternatives=[
            IDRSTextElementAlternative(text="b2", confidence=2),
            IDRSTextElementAlternative(text="b3", confidence=2),
            IDRSTextElementAlternative(text="b4", confidence=2),
            IDRSTextElementAlternative(text="b5", confidence=2),
        ]),
        IDRSTextElement(text="c1", confidence=0, alternatives=[
            IDRSTextElementAlternative(text="c2", confidence=2),
            IDRSTextElementAlternative(text="c3", confidence=2),
            IDRSTextElementAlternative(text="c4", confidence=2),
            IDRSTextElementAlternative(text="c5", confidence=2),
        ]),
    ])

    text_alternatives = word_additional_data.get_text_alternatives(max_confidence_loss=6)
    assert len(text_alternatives) == mim_ocr_cfg.ocr.ocr_backend_parameters.postprocessing.alternatives.\
        max_nr_of_line_alternatives
