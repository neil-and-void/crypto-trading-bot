from typing import *
from collections import deque

from src.constants import *


class NeilBot():
    def __init__(self, **kwargs):
        """ initialize bot with config kwargs and initial state

        ! If you change the strategy, config kwargs will need to change too

        Args:
            **long_smoothing (int): Long EMA smoothing constant
            **long_ema_period (int): Length of the long EMA period
            **short_smoothing (int): Short EMA smoothing constant
            **short_ema_period (int): Length of the short EMA period
            **rsi_period (int): Length of the RSI lookback
            **rsi_threshold (float): Threshold value for RSI
        """
        # config variables
        self._long_smoothing = kwargs['long_smoothing']
        self._long_ema_period = kwargs['long_ema_period']
        self._short_smoothing = kwargs['short_smoothing']
        self._short_ema_period = kwargs['short_ema_period']
        self._rsi_period = kwargs['rsi_period']
        self._rsi_threshold = kwargs['rsi_threshold']
        # state variables
        self._prev_long_ema = 0
        self._prev_short_ema = 0
        self._prev_gains = None
        self._prev_losses = None

    def _ema(self, price, prev_ema, smoothing, period):
        """ get the ema of the current period

        Args:
            price (float): Closing price of coin
            prev_ema (float): Previously computed EMA
            smoothing (int): Smoothing constant
            period (int): period length of EMA

        Returns:
            float: EMA as a float
        """
        return (price * (smoothing / (1 + period))) + (prev_ema * (1 - (smoothing / (1 + period))))

    def _rsi(self, ohlc, prev_gains, prev_losses):
        """ get rsi of the current period

        Args:
            ohlc (List): Array of ohlc data
            prev_gains (deque): deque of a window of the gains in the the last period length of ohlc data
            prev_losses (deque): deque of a window of the losses in the the last period length of ohlc data 

        Returns:
            float: float value representing the RSI
        """
        open = float(ohlc[BUY])
        close = float(ohlc[CLOSE])
        # slide window forward
        if close < open:
            self._prev_losses.append(open - close)
            self._prev_gains.append(0)
        elif open < close:
            self._prev_gains.append(close - open)
            self._prev_losses.append(0)
        self._prev_gains.popleft()
        self._prev_losses.popleft()

        relative_strength = (sum(prev_gains) / sum(prev_losses))
        return 100 - (100 / (1 + relative_strength))

    def initialize_values(self, ohlc_data):
        """ populate state with initial values needed for indicators

        Args:
            ohlc_data (List): Array of OHLC data
        """
        # initial ema step
        self._prev_short_ema = sum([float(ohlc[CLOSE])
                                    for ohlc in ohlc_data[-self._short_ema_period:]]) / self._short_ema_period
        self._prev_long_ema = sum([float(ohlc[CLOSE])
                                   for ohlc in ohlc_data[-self._long_ema_period:]]) / self._long_ema_period
        # initial rsi step, use deque for sliding window
        self._prev_gains = deque()
        self._prev_losses = deque()
        for ohlc in ohlc_data[-self._rsi_period:]:
            close = float(ohlc[CLOSE])
            open = float(ohlc[OPEN])
            if open < close:
                self._prev_gains.append(close - open)
                # ensures same window length as prev gains
                self._prev_losses.append(0)
            elif close < open:
                self._prev_losses.append(abs(close - open))
                # ensures same window length as prev losses
                self._prev_gains.append(0)

    def analyze(self, ohlc) -> None:
        """ Analyze for the occurrence of a buy or sell signal for this ohlc

        ! Implement your custom strategy by replacing the body of this method

        Args:
            ohlc (List): ohlc of the current period

        Returns:
            int: Buy or sell constant to indicate action to be taken
        """
        long_ema = self._ema(
            float(ohlc[CLOSE]), self._prev_long_ema, self._long_smoothing, self._long_ema_period)
        short_ema = self._ema(
            float(ohlc[CLOSE]), self._prev_short_ema, self._short_smoothing, self._short_ema_period)
        rsi = self._rsi(ohlc, self._prev_gains, self._prev_losses)

        # update previous EMA's for next calculation
        self._prev_short_ema = short_ema
        self._prev_long_ema = long_ema

        # Check rsi first to ensure that it has crossed before ema values have crossed
        if rsi > self._rsi_threshold and long_ema < short_ema:
            return BUY
        elif long_ema > short_ema or rsi < self._rsi_threshold:
            return SELL
