from enum import Enum, auto


class LoginType(Enum):
    UNKNOWN = auto()
    CUFS = auto()
    ADFS = auto()
    ADFSLight = auto()
    ADFSLightScoped = auto()
    ADFSLightCards = auto()
