from typing import *
import sched
import time
from datetime import datetime, date, timedelta
import requests
import urllib.parse
import hashlib
import hmac
import mplfinance as mpf
import pandas as pd
import json
import base64
import matplotlib.pyplot as plt
import numpy as np
import os
from os.path import join, dirname
from dotenv import load_dotenv

from src.constants import *
from src.constants import OHLC
from krakenex.api import API


class NeilBot():
    def __init__(self, client: API, pair: str):
        """Inits NeilBot with an API client

        :param client: client to interface with a coin exchange
        :type client: API
        :param pair: coin-currency pair according to Kraken's naming scheme ex. Ethereum in USD = 'XETHZUSD'
        :type pair: str
        """
        self.client = client
        self.pair = pair
        self.backtestResults = {}

    def _buy(self) -> None:
        pass

    def _sell(self) -> None:
        pass

    def _analyze(self) -> None:
        # check for sell off limit

        # check for buy signal

        # check for sell signal
        pass

    def _queryOHLC(self, days) -> dict:
        interval = 60  # 1 hour in minutes
        today = datetime.today()
        periodLen = timedelta(days=days)
        period = today - periodLen
        periodTimeStamp = int(period.timestamp())
        return self.client.query_public(
            f'OHLC?pair={self.pair}&interval={interval}&since={periodTimeStamp}')

    def backtest(self, hours) -> dict:
        """backtest the strategy and get results for it

        :param days: number of days to backtest over from today
        :type days: int
        """
        response = self._queryOHLC(hours)
        hourly = response['result'][self.pair]
        print(len(hourly))

        hourlyClose = np.array([hourOHLC[OHLC.close] for hourOHLC in hourly])
        print(hourlyClose)

        # compute initial long and short EMA ie. the respective SMA's
        longEMA = sum([float(hourly[hour][OHLC.close])
                       for hour in range(LONG_EMA_LEN)]) / LONG_EMA_LEN
        shortEMA = sum([float(hourly[hour][OHLC.close])
                        for hour in range(SHORT_EMA_LEN, LONG_EMA_LEN)]) / SHORT_EMA_LEN
        longSmoothingFactor = SMOOTHING_FACTOR / (1 + LONG_EMA_LEN)
        shortSmoothingFactor = SMOOTHING_FACTOR / (1 + SHORT_EMA_LEN)

        longEMAVals = np.empty(hours)
        shortEMAVals = np.empty(hours)
        longEMAVals[LONG_EMA_LEN - 1] = longEMA
        shortEMAVals[LONG_EMA_LEN - 1] = shortEMA

        coinQty = 0
        wallet = initialWallet = 100
        bought = False
        for hourIdx in range(LONG_EMA_LEN, hours):
            closePrice = float(hourly[hourIdx][OHLC.close])
            shortEMA = (shortEMA * (1 - shortSmoothingFactor) +
                        (closePrice * shortSmoothingFactor))
            longEMA = (longEMA * (1 - longSmoothingFactor) +
                       (closePrice * longSmoothingFactor))

            # buy signal
            if not bought and shortEMA > longEMA:
                coinQty = wallet / closePrice
                bought = True

            # sell signal
            if bought and longEMA > shortEMA:
                wallet = coinQty * closePrice
                bought = False

            longEMAVals[hourIdx] = longEMA
            shortEMAVals[hourIdx] = shortEMA
        print('result', wallet)
        self.backtestResults = {
            'longEMAVals': longEMAVals,
            'shortEMAVals': shortEMAVals,
            'wallet': wallet
        }

    def plot(self, hours) -> None:
        """plot the long and short EMA's on an OHLC candlestick mpl plot

        :param days: number of days to backtest over from today
        :type days: int
        """
        self.backtest(hours)
        response = self._queryOHLC(hours)
        hourly = response['result'][self.pair]
        for hourIdx in range(len(hourly)):
            hourly[hourIdx][0] = datetime.fromtimestamp(hourly[hourIdx][0])
            for i in range(1, 8):
                hourly[hourIdx][i] = float(hourly[hourIdx][i])

        labels = [label.name for label in OHLC]
        labels[OHLC.time] = 'Date'
        df = pd.DataFrame(columns=labels, data=hourly)
        df.index = pd.DatetimeIndex(df['Date'])

        # plot EMA, buy and sell vals on OHLC plot
        ap = [
            mpf.make_addplot(self.backtestResults['longEMAVals'],
                             color='blue', type='line'),
            mpf.make_addplot(self.backtestResults['shortEMAVals'],
                             color='orange', type='line'),
            # mpf.make_addplot(sellVals, color='red',
            #                  type='scatter', markersize=75),
            # mpf.make_addplot(buyVals, color='green',
            #                  type='scatter', markersize=75)
        ]
        mpf.plot(df, type='candle', show_nontrading=True,
                 style='ibd', addplot=ap)

    def run(self) -> None:
        while True:
            self._analyze()
