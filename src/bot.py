from typing import *
import schedule
from datetime import datetime, date, timedelta
import pandas as pd
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from src.constants import *
from krakenex.api import API


class NeilBot():
    def __init__(self, client: API, pair: str):
        """Inits NeilBot with an API client and coin-currency pair

        :param client: client to interface with a coin exchange
        :type client: API
        :param pair: coin-currency pair according to Kraken's naming scheme ex. Ethereum in USD = 'XETHZUSD'
        :type pair: str
        """
        self.client = client
        self.pair = pair
        self.backtestResults = {}
        self.state = {}

    def _buy(self) -> None:
        """ Sell
        """
        data = {
            "ordertype": "market",
            "type": "buy",
            "pair": self.pair
        }
        response = self.client.query_private('AddOrder', data=data)
        print(response['result']['descr']['order'])

    def _sell(self) -> None:
        """ Sell
        """
        data = {
            "ordertype": "market",
            "type": "sell",
            "pair": self.pair
        }
        response = self.client.query_private('AddOrder', data=data)
        print(response['result']['descr']['order'])

    def _analyze(self, ohlc) -> None:
        """
        Analyze for the occurrence of a buy or sell signal with the current state and ohlc data
        """
        # query for latest day ohlc

        # compute EMA

        # check for sell off limit

        # check for buy signal

        # check for sell signal
        print('analyze')

    def _queryOHLC(self, days) -> dict:
        """get OHLC period data of length days

        :param days: [description]
        :type days: [type]
        :return: [description]
        :rtype: dict
        """
        interval = 1440  # 1 hour in minutes
        today = datetime.today()
        periodLen = timedelta(days=days)
        period = today - periodLen
        periodTimeStamp = int(period.timestamp())
        return self.client.query_public(
            f'OHLC?pair={self.pair}&interval={interval}&since={periodTimeStamp}')

    def _ema(self, periodIdx, close, periodLen, smoothing) -> float:
        """ Compute ema

        :param dayIdx: [description]
        :type dayIdx: [type]
        :param periodData: [description]
        :type periodData: [type]
        :param periodLen: [description]
        :type periodLen: [type]
        :param smoothing: [description]
        :type smoothing: [type]
        :return: [description]
        :rtype: float
        """
        # base: compute SMA as initial EMA
        if periodIdx == periodLen - 1:
            return sum([close[i] for i in range(periodLen)]) / periodLen

        # recursive:
        else:
            return (close[periodIdx] * smoothing) + \
                (self._ema(periodIdx - 1, close, periodLen, smoothing) * (1 - smoothing))

    def backtest(self, days) -> dict:
        """backtest the strategy and get results for it

        :param days: number of days to backtest over from today
        :type days: int
        """
        response = self._queryOHLC(days)
        daily = response['result'][self.pair]

        dailyClose = np.array([float(dayOHLC[OHLC.close])
                               for dayOHLC in daily])

        # compute initial long and short EMA ie. the respective SMA's
        longEMA = sum(dailyClose[:LONG_EMA_LEN]) / LONG_EMA_LEN
        shortEMA = sum(
            dailyClose[SHORT_EMA_LEN: LONG_EMA_LEN]) / (LONG_EMA_LEN - SHORT_EMA_LEN)

        longSmoothing = SMOOTHING_FACTOR / (1 + LONG_EMA_LEN)
        shortSmoothing = SMOOTHING_FACTOR / (1 + SHORT_EMA_LEN)

        longEMAVals = np.array([None for i in range(days)])
        shortEMAVals = np.array([None for i in range(days)])
        longEMAVals[LONG_EMA_LEN - 1] = longEMA
        shortEMAVals[LONG_EMA_LEN - 1] = shortEMA

        coinQty = 0
        wallet = initialWallet = 200
        bought = False
        buyPrice = 0
        crossed = False
        crossCount = 9
        minCross = 2
        buys = np.array([None for i in range(days)])
        sells = np.array([None for i in range(days)])
        for dayIdx in range(LONG_EMA_LEN, days):
            closePrice = float(daily[dayIdx][OHLC.close])
            shortEMA = (shortEMA * (1 - shortSmoothing) +
                        (closePrice * shortSmoothing))
            longEMA = (longEMA * (1 - longSmoothing) +
                       (closePrice * longSmoothing))

            # longEMA = self._ema(dayIdx, dailyClose,
            #                     LONG_EMA_LEN, longSmoothing)
            # shortEMA = self._ema(dayIdx, dailyClose,
            #                      SHORT_EMA_LEN, shortSmoothing)

            # buy signal
            if not bought and longEMA < shortEMA:
                if minCross < crossCount:
                    coinQty = wallet / closePrice
                    buys[dayIdx] = closePrice
                    buyPrice = closePrice
                    bought = True
                crossCount += 1

            # sell signal or stop loss at 10%
            if bought and (shortEMA < longEMA or coinQty * closePrice < 0.9 * (coinQty * buyPrice)):
                if minCross < crossCount:
                    wallet = coinQty * closePrice
                    sells[dayIdx] = closePrice
                    bought = False
                crossCount += 1

            longEMAVals[dayIdx] = longEMA
            shortEMAVals[dayIdx] = shortEMA
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

    def plot(self, days) -> None:
        """plot the long and short EMA's on an OHLC candlestick mpl plot

        :param days: number of days to backtest over from today
        :type days: int
        """
        results = self.backtest(days)
        response = self._queryOHLC(days)
        daily = response['result'][self.pair]
        dailyClose = np.array([float(dayOHLC[OHLC.close])
                               for dayOHLC in daily])
        times = np.array([datetime.utcfromtimestamp(dayOHLC[OHLC.time]).strftime('%b %d %y %H:%M')
                         for dayOHLC in daily])

        fig, ax = plt.subplots()

        plt.xlabel('Dates (UTC)')
        plt.ylabel(f'Hourly closing prices ({self.pair})')
        plt.plot(times, dailyClose,
                 label=f"{self.pair} close price", color="black")
        plt.plot(times, results['longEMAVals'],
                 label=f"{LONG_EMA_LEN} EMA", color="blue")
        plt.plot(times, results['shortEMAVals'],
                 label=f"{SHORT_EMA_LEN} EMA", color="orange")
        plt.plot(times, results['buys'],
                 label="Buy Indicator", marker=".", linestyle='None', color="green", markersize=10)
        plt.plot(times, results['sells'],
                 label="Sell Indicator", marker=".", linestyle='None', color="red", markersize=10)

        plt.legend()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(days // 12))
        plt.grid()
        fig.autofmt_xdate()
        ax.autoscale()
        plt.title(
            f'EMA 10/5 Day Cross with Buy and Sell Indicators for {self.pair}')
        plt.show()

    def run(self) -> None:
        # initialize state with past month of data
        # compute initial long and short EMA ie. the respective SMA's
        longEMA = sum(dailyClose[:LONG_EMA_LEN]) / LONG_EMA_LEN
        shortEMA = sum(
            dailyClose[SHORT_EMA_LEN: LONG_EMA_LEN]) / (LONG_EMA_LEN - SHORT_EMA_LEN)
        longSmoothingFactor = SMOOTHING_FACTOR / (1 + LONG_EMA_LEN)
        shortSmoothingFactor = SMOOTHING_FACTOR / (1 + SHORT_EMA_LEN)

        self.state = {
            'longEMA': longEMA,
            'shortEMA': shortEMA
        }

        schedule.every(1).seconds.do(self._analyze)
        # schedule.every().day.at("18:00").do(self._analyze)
        while True:
            schedule.run_pending()
            time.sleep(1)
