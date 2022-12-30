from enum import Enum


class PoktChainID(str, Enum):
    POKT = "0001"
    NEAR = "0052"
    DFK = "03DF"
    SWIMMER = "03CB"
    AVAX = "0003"
    AVAXP = "0003-P"
    AVAXC = "0003-C"
    AVAXX = "0003-X"
