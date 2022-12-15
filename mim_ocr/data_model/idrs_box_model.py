import dataclasses
from typing import List, Optional, NamedTuple

from mim_ocr import mim_ocr_cfg, mim_ocr_cfg_required


@dataclasses.dataclass
class IDRSTextElementStyle:
    font_size: int
    font_name: str
    font_stretch: int
    bold: bool
    italic: bool
    underline: bool
    subscript: bool
    superscript: bool

    @staticmethod
    def from_json(text_element_style_json):
        return IDRSTextElementStyle(
            font_size=text_element_style_json["font_size"],
            font_name=text_element_style_json["font_name"],
            font_stretch=text_element_style_json["font_stretch"],
            bold=bool(text_element_style_json["bold"]),
            italic=bool(text_element_style_json["italic"]),
            underline=bool(text_element_style_json["underline"]),
            subscript=bool(text_element_style_json["subscript"]),
            superscript=bool(text_element_style_json["superscript"]),
        )


@dataclasses.dataclass
class IDRSTextElementAlternative:
    text: str
    confidence: int

    @staticmethod
    def from_json(text_element_alternative_json):
        text = ""
        for character in text_element_alternative_json["idrs_characters"]:
            try:
                text += chr(character)
            except OverflowError:
                pass  # TODO: add some utf-16 handling
        return IDRSTextElement(
            confidence=text_element_alternative_json["confidence"],
            text=text
        )


@dataclasses.dataclass
class IDRSTextElement:
    confidence: int
    text: str
    style: Optional[IDRSTextElementStyle] = None
    alternatives: List[IDRSTextElementAlternative] = dataclasses.field(default_factory=lambda: [])

    @staticmethod
    def from_json(text_element_json):
        text = ""
        for character in text_element_json["idrs_characters"]:
            try:
                text += chr(character)
            except OverflowError:
                pass  # TODO: add some utf-16 handling
        return IDRSTextElement(
            confidence=text_element_json["confidence"],
            text=text,
            alternatives=[IDRSTextElementAlternative.from_json(alternative_json)
                          for alternative_json in text_element_json["alternatives"]],
            style=IDRSTextElementStyle.from_json(text_element_json["style"])
        )


class IDRSWordAlternative(NamedTuple):
    """structure that contains an alternative for whole word
         - string with word text alternative
         - sum of confidence loss in IDRS scale (0-most confident 255-no confidence)
         - list containing indexes of chosen alterantives for each text_element (-1 for main text_element)"""
    text: str
    confidence_loss: int
    text_elements_alternatives: List[int]


# IDRS Stores most of word data in structure containing list of text element. This model represents this structure.
@dataclasses.dataclass
class IDRSWordAdditionalData:
    text_elements: List[IDRSTextElement]

    @staticmethod
    def from_json(word_json):
        return IDRSWordAdditionalData(
            [IDRSTextElement.from_json(text_element_json) for text_element_json in word_json["idrs_text_elements"]])

    def get_text(self):
        return "".join([text_element.text for text_element in self.text_elements])

    def get_confidence(self):
        return (255-sum([text_element.confidence for text_element in self.text_elements])/len(self.text_elements))/2.55

    @mim_ocr_cfg_required
    def get_text_alternatives(self, max_confidence_loss: int = -1) -> List[IDRSWordAlternative]:
        # List of alternatives that will be for each iteration extended by adding new variants from next text element
        # alternatives
        max_nr_of_line_alternatives = mim_ocr_cfg.ocr.ocr_backend_parameters.postprocessing.alternatives.\
            max_nr_of_line_alternatives

        current_alternatives = [IDRSWordAlternative(text="",
                                                    confidence_loss=0,
                                                    text_elements_alternatives=[])]
        for text_element in self.text_elements:
            new_current_alternatives: List[IDRSWordAlternative] = []
            base_text_element_confidence = text_element.confidence
            for (current_alternative_text, current_alternative_confidence_loss, current_alternative_indexes) \
                    in current_alternatives:
                new_current_alternatives.append(IDRSWordAlternative(
                    text=current_alternative_text+text_element.text,
                    confidence_loss=current_alternative_confidence_loss,
                    text_elements_alternatives=current_alternative_indexes+[-1]
                ))
            for (i, text_element_alternative) in enumerate(text_element.alternatives):
                for (current_alternative_text, current_alternative_confidence_loss, current_alternative_indexes) \
                        in current_alternatives:

                    if len(new_current_alternatives) >= max_nr_of_line_alternatives:
                        break

                    sum_confidence_loss = current_alternative_confidence_loss + text_element_alternative.confidence - \
                        base_text_element_confidence
                    if max_confidence_loss == -1 or sum_confidence_loss <= max_confidence_loss:
                        new_current_alternatives.append(IDRSWordAlternative(
                             text=current_alternative_text + text_element_alternative.text,
                             confidence_loss=sum_confidence_loss,
                             text_elements_alternatives=current_alternative_indexes+[i]))

            current_alternatives = new_current_alternatives

        return current_alternatives
