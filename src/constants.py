from enum import IntEnum


class OHLC(IntEnum):
    """
    names with the corresponding indices of data in OHLC response data from Coinbase API
    """
    time = 0
    low = 1
    high = 2
    open = 3
    close = 4
    volume = 5


SHORT_EMA_LEN = 5
LONG_EMA_LEN = 13
SMOOTHING_FACTOR = 2

TWENTY_FOUR_HOURS = 3600  # minutes
