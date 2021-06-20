from enum import IntEnum


class OHLC(IntEnum):
    """
    names with the corresponding indices of data in OHLC response data from Kraken API
    """
    time = 0
    open = 1
    high = 2
    low = 3
    close = 4
    vwap = 5
    volume = 6
    count = 7


SHORT_EMA_LEN = 5
LONG_EMA_LEN = 13
SMOOTHING_FACTOR = 2
