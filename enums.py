from enum import Enum


class Section(str, Enum):
    B1 = "B.1"
    B2 = "B.2"


class INIDCode(str, Enum):
    REGISTRATION_NUMBER = "111"
    REGISTRATION_DATE = "151"
    PUBLICATION_DATE = "450"
    TRADEMARK_NUMBER = "210"
    PRIOR_REGISTRATION = "400"
