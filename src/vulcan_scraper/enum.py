from enum import Enum, auto


class LoginType(Enum):
    UNKNOWN = auto()
    CUFS = auto()
    ADFS = auto()
    ADFSCards = auto()
    ADFSLight = auto()
