from abc import ABC, abstractmethod
from typing import *


class Strategy(ABC):
    @abstractmethod
    def evaluate(self, data):
        pass


class EMAC_10_5_D(Strategy):
    """
    [E]xponential [M]oving [A]verage [C]rossover [10]-[5] [D]ay strategy
    """

    def __init__(self):
        pass

    def evaluate(self, data):
        """ TODO: determine whether or not the agent should buy or sell

        :param data: [description]
        :type data: [type]
        """
        # initialize variables for backtesting
        timeFrameLen = len(dailyOHLC)

        longEMA = 0
        prevLongEMA = 0
        longLeft = 0
        longRight = LONG_EMA_LEN - 1
        longSmoothingFactor = SMOOTHING_FACTOR / (1 + LONG_EMA_LEN)

        shortEMA = 0
        prevShortEMA = 0
        shortLeft = LONG_EMA_LEN - SHORT_EMA_LEN - 1
        shortRight = LONG_EMA_LEN - 1
        shortSmoothingFactor = SMOOTHING_FACTOR / (1 + SHORT_EMA_LEN)

        # compute initial short and long EMA's
        dayIdx = 0
        for dayIdx in range(LONG_EMA_LEN):
            # compute long EMA
            longEMA += (prevLongEMA * (1 - longSmoothingFactor)) + \
                (float(dailyOHLC[dayIdx][OHLC_Data.close])
                 * longSmoothingFactor)
            prevLongEMA = longEMA

            # compute short EMA
            if (SHORT_EMA_LEN - 1) < dayIdx:
                shortEMA += (prevShortEMA * (1 - shortSmoothingFactor)) + \
                    (float(dailyOHLC[dayIdx][OHLC_Data.close])
                     * shortSmoothingFactor)
                prevShortEMA = shortEMA

        funds = originalFunds = 100
        ethQty = 0
        bought = False
        dayIdx += 1
        while dayIdx < timeFrameLen:
            longEMA -= (float(dailyOHLC[dayIdx - LONG_EMA_LEN]
                        [OHLC_Data.close]) * longSmoothingFactor)
            longEMA = (longEMA * (1 - longSmoothingFactor) +
                       (float(dailyOHLC[dayIdx][OHLC_Data.close]) * longSmoothingFactor))

            shortEMA -= (float(dailyOHLC[dayIdx - SHORT_EMA_LEN]
                               [OHLC_Data.close]) * shortSmoothingFactor)
            shortEMA = (shortEMA * (1 - shortSmoothingFactor) +
                        (float(dailyOHLC[dayIdx][OHLC_Data.close]) * shortSmoothingFactor))
            # print(
            #     f'{float(dailyOHLC[dayIdx][OHLC_Data.close])} | {longEMA} | {shortEMA}')
            dayIdx += 1
