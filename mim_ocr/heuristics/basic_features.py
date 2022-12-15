from .regex_feature import RegexFeature


PHONE_NUMBER_FEATURE = RegexFeature(name="PhoneNumber",
                                    core_regex=r"\(?\d{2}\)?(?:(?:[- ])?\d){7}",
                                    before_regex=r"\s|^|:",
                                    after_regex=r"\s|$",
                                    priority=7)

"""NUMBER FEATURE maps not only numbers, but also numeric expressions, like <=10 >7"""
NUMBER_FEATURE = RegexFeature(name="Number",
                              core_regex=r"(?:|>|<|=|>=|<=)\d+(?:(?:\.|,)?)\d+",
                              before_regex=r"\s|^",
                              after_regex=r"\s|$",
                              priority=5)


DATE_FEATURE = RegexFeature(
    name="Date",
    core_regex=r'(0[1-9]|1[0-9]|2[0-9]|3[0-1])(-|.|/)(0[1-9]|1[0-2])(-|.|/)([12][90][0-9][0-9])'
               r'|'
               r'([12][90][0-9][0-9])-(0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-9]|3[0-1])',
    before_regex=r"\s|^|:",
    after_regex=r"\s|$|,|;",
    priority=8
)
