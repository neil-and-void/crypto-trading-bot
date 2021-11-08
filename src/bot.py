from typing import *
from datetime import datetime as dt
import time

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from src import constants


class NeilBot():
    def __init__(self, **kwargs):
        """ Initialize NeilBot with config
        """
        self.smoothing = kwargs['smoothing']
        self.ema_period = kwargs['ema_period']
        self.rsi_period = kwargs['rsi_period']
        self.state = {
            "prev_ema": 0,
            "prev_avg_gain": 0,
            "prev_avg_loss": 0,
            "buy_price": 0,
            "crosses": 0
        }

    def _ema(self, price, prev_ema):
        return (price * (self.smoothing / (1 + self.ema_period))) + (prev_ema * (1 - (self.smoothing / (1 + self.ema_period))))

    def _rsi(self, price, prev_avg_gain, prev_avg_loss):
        relative_strength = (prev_avg_gain + price) / (prev_avg_loss + price)
        return 100 - (100 / (1 + relative_strength))

    def initialize_values(self, ohlc_data):
        self.state['prev_ema'] = sum([float(ohlc[constants.CLOSE])
                                     for ohlc in ohlc_data[-self.ema_period:]]) / self.ema_period
        gains = []
        losses = []
        prev_close = float(ohlc_data[-self.rsi_period][constants.CLOSE])
        for ohlc in ohlc_data[-self.rsi_period + 1:]:
            close = float(ohlc[constants.OPEN])
            # gained
            if prev_close < close:
                gains.append(close - prev_close)
            # lost
            if prev_close > close:
                losses.append(abs(close - prev_close))
            prev_close = close
        self.state['avg_loss'] = sum(losses) / self.rsi_period
        self.state['avg_gain'] = sum(gains) / self.rsi_period

    def analyze(self, ohlc) -> None:
        """
        Analyze for the occurrence of a buy or sell signal for this period
        """
        ema = self._ema(float(ohlc[constants.CLOSE]), self.state['prev_ema'])
        rsi = self._rsi(
            float(ohlc[constants.CLOSE]), self.state['prev_avg_gain'], self.state['prev_avg_loss'])
        print(ema, rsi)

    def backtest(self, days) -> Dict:
        """backtest the strategy and get results for it

        :param days: number of days to backtest over from today
        :type days: int
        """
        daily = self._queryOHLC(days)

        dailyClose = np.array([float(dayOHLC[OHLC.close])
                               for dayOHLC in daily])

        # compute initial long and short EMA ie. the respective SMA's
        longEMA = sum(
            dailyClose[:self.config["longEMALen"]]) / self.config["longEMALen"]
        shortEMA = sum(
            dailyClose[(self.config["longEMALen"]) - (self.config["shortEMALen"]): self.config["longEMALen"]]) / self.config["shortEMALen"]

        longSmoothing = SMOOTHING_FACTOR / (1 + self.config["longEMALen"])
        shortSmoothing = SMOOTHING_FACTOR / (1 + self.config["shortEMALen"])

        longEMAVals = np.array([None for i in range(days)])
        shortEMAVals = np.array([None for i in range(days)])
        longEMAVals[self.config["longEMALen"]] = longEMA
        shortEMAVals[self.config["longEMALen"]] = shortEMA

        coinQty = 0
        wallet = initialWallet = 200
        bought = False
        buyPrice = 0
        crossed = False
        crossCount = 0
        minCross = 2
        buys = np.array([None for i in range(days)])
        sells = np.array([None for i in range(days)])
        for dayIdx in range(self.config["longEMALen"]+1, days):
            closePrice = float(daily[dayIdx][OHLC.close])
            shortEMA = (shortEMA * (1 - shortSmoothing) +
                        (closePrice * shortSmoothing))
            longEMA = (longEMA * (1 - longSmoothing) +
                       (closePrice * longSmoothing))
            longEMAVals[dayIdx] = longEMA
            shortEMAVals[dayIdx] = shortEMA

            # count amount of times a cross has occurred
            prevDayIdx = dayIdx - 1
            if (shortEMAVals[prevDayIdx] < longEMAVals[prevDayIdx] and longEMA < shortEMA) \
                    or (longEMAVals[prevDayIdx] < shortEMAVals[prevDayIdx] and shortEMA < longEMA):
                crossCount += 1

            # wait for 2 crosses before entering market
            if crossCount < minCross:
                continue

            # buy signal
            if not bought and longEMA < shortEMA:
                if minCross < crossCount:
                    coinQty = wallet / closePrice
                    buys[dayIdx] = closePrice
                    buyPrice = closePrice
                    bought = True

            # sell signal or stop loss at 10%
            if bought and (shortEMA < longEMA
                           or coinQty * closePrice < 0.9 * (coinQty * buyPrice)):
                if minCross < crossCount:
                    wallet = coinQty * closePrice
                    sells[dayIdx] = closePrice
                    bought = False

        if bought:
            wallet = coinQty * closePrice
        return {
            'longEMAVals': longEMAVals,
            'shortEMAVals': shortEMAVals,
            'buys': buys,
            'sells': sells,
            'initialWallet': initialWallet,
            'wallet': wallet,
        }
