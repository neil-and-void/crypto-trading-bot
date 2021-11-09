from typing import *
from datetime import datetime as dt
import time

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from src import constants


class NeilBot():
    def __init__(self, **kwargs):
        """ initialize bot with config kwargs and initial state
        """
        self._long_smoothing = kwargs['long_smoothing']
        self._long_ema_period = kwargs['long_ema_period']
        self._short_smoothing = kwargs['short_smoothing']
        self._short_ema_period = kwargs['short_ema_period']
        self._rsi_period = kwargs['rsi_period']
        self._rsi_threshold = kwargs['rsi_threshold']
        self._state = {
            "prev_long_ema": 0,
            "prev_short_ema": 0,
            "prev_avg_gain": 0,
            "prev_avg_loss": 0,
            "prev_price": 0
        }

    def _ema(self, price, prev_ema, smoothing, period):
        """ get the ema of the current period

        :param price: [description]
        :param prev_ema: [description]
        :return: float value representing the EMA
        """
        return (price * (smoothing / (1 + period))) + (prev_ema * (1 - (smoothing / (1 + period))))

    def _rsi(self, ohlc, prev_avg_gain, prev_avg_loss):
        """ get rsi of the current period

        :param price: [description]
        :param prev_avg_gain: [description]
        :param prev_avg_loss: [description]
        :return: float value representing the RSI
        """
        open = float(ohlc[constants.BUY])
        close = float(ohlc[constants.CLOSE])
        cur_gain = 0
        cur_loss = 0
        if close < open:
            cur_gain = open - close
        elif open > close:
            cur_loss = abs(open - close)
        relative_strength = ((prev_avg_gain * 13) + cur_gain) / \
            ((prev_avg_loss * 13) + cur_loss)
        return 100 - (100 / (1 + relative_strength))

    def initialize_values(self, ohlc_data):
        """ perform initial calculations for indicators

        :param ohlc_data: Array of OHLC data
        """
        # initial ema step
        self._state['prev_short_ema'] = sum([float(ohlc[constants.CLOSE])
                                             for ohlc in ohlc_data[-self._short_ema_period:]]) / self._short_ema_period

        self._state['prev_long_ema'] = sum([float(ohlc[constants.CLOSE])
                                            for ohlc in ohlc_data[-self._long_ema_period:]]) / self._long_ema_period
        # RSI step 1
        gains = []
        losses = []
        for ohlc in ohlc_data[-self._rsi_period:]:
            close = float(ohlc[constants.CLOSE])
            open = float(ohlc[constants.OPEN])
            # gained
            if open < close:
                gains.append(close - open)
            # lost
            elif close < open:
                losses.append(abs(close - open))
        self._state['prev_avg_loss'] = sum(losses) / self._rsi_period
        self._state['prev_avg_gain'] = sum(gains) / self._rsi_period

    def analyze(self, ohlc) -> None:
        """ Analyze for the occurrence of a buy or sell signal for this period

        :return: Buy or sell constant to indicate action to be taken
        """
        long_ema = self._ema(
            float(ohlc[constants.CLOSE]), self._state['prev_long_ema'], self._long_smoothing, self._long_ema_period)
        self._state['prev_long_ema'] = long_ema
        short_ema = self._ema(
            float(ohlc[constants.CLOSE]), self._state['prev_short_ema'], self._short_smoothing, self._short_ema_period)
        self._state['prev_short_ema'] = short_ema
        rsi = self._rsi(
            ohlc, self._state['prev_avg_gain'], self._state['prev_avg_loss'])
        # compute signal based on strategy
        if short_ema > long_ema and rsi > self._rsi_threshold:
            return constants.BUY
        elif long_ema < short_ema or rsi < self._rsi_threshold:
            return constants.SELL
