from typing import *
import schedule
from datetime import datetime as dt, date, timedelta
import pandas as pd
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import cbpro

from src.constants import *


class NeilBot():
    def __init__(self, config: dict, publicClient: cbpro.PublicClient, authenticatedClient: cbpro.AuthenticatedClient):
        """Inits NeilBot with an API client and coin-currency pair"""
        self.config = config
        self.publicClient = publicClient
        self.authenticatedClient = authenticatedClient
        self.state = {}

    def _buy(self) -> None:
        """ buy
        """
        data = {
            "ordertype": "market",
            "type": "buy",
            "pair": self.pair
        }
        response = self.client.query_private('AddOrder', data=data)
        self.state['bought'] = True
        print(response)
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
        print(response)
        self.state['bought'] = False
        print(response['result']['descr']['order'])

    def _analyze(self) -> None:
        """
        Analyze for the occurrence of a buy or sell signal for today
        """
        response = self._queryOHLC(1)  # past day OHLC
        pastDay = response['result'][self.pair]
        print(self.state)
        print(pastDay)

        # query for latest day ohlc
        longSmoothing = SMOOTHING_FACTOR / (1 + LONG_EMA_LEN)
        shortSmoothing = SMOOTHING_FACTOR / (1 + SHORT_EMA_LEN)

        # compute EMA's
        closePrice = float(pastDay[0][OHLC.close])
        shortEMA = (self.state['shortEMA'] * (1 - shortSmoothing) +
                    (closePrice * shortSmoothing))
        longEMA = (self.state['longEMA'] * (1 - longSmoothing) +
                   (closePrice * longSmoothing))

        # check for buy signal
        if not self.state['bought'] and longEMA < shortEMA:
            print('buy')
            self._buy()

        # sell signal or stop loss at 10%
        if self.state['bought'] and (shortEMA < longEMA or coinQty * closePrice < 0.9 * (coinQty * buyPrice)):
            print('buy')
            self._sell()

        # check for sell signal or stop loss

    def _queryOHLC(self, days=200) -> list[list[OHLC]]:
        """get OHLC data between the period of start and end
        """
        today = dt.utcnow().today()
        end = today.date()

        t_delta = timedelta(days=days-1)

        start = today - t_delta
        start = start.date()

        return self.publicClient.get_product_historic_rates('ETH-USD', granularity=86400, start=start, end=end)

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
        daily = self._queryOHLC(days)

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
        crossCount = 0
        minCross = 2
        buys = np.array([None for i in range(days)])
        sells = np.array([None for i in range(days)])
        for dayIdx in range(LONG_EMA_LEN, days):
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
            if bought and (shortEMA < longEMA or coinQty * closePrice < 0.9 * (coinQty * buyPrice)):
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

    def plot(self, days) -> None:
        """plot the long and short EMA's on an OHLC candlestick mpl plot

        :param days: number of days to backtest over from today
        :type days: int
        """
        results = self.backtest(days)
        daily = self._queryOHLC(days)
        dailyClose = np.array([float(dayOHLC[OHLC.close])
                               for dayOHLC in daily])
        print(len(daily))
        times = np.array([dt.utcfromtimestamp(dayOHLC[OHLC.time]).strftime('%b %d %y %H:%M')
                         for dayOHLC in daily])

        fig, ax = plt.subplots()

        # print(len(results['longEMAVals']), len(results['shortEMAVals']), len(
        #     results['buys']), len(results['sells']), len(times))
        plt.xlabel('Dates (UTC)')
        plt.ylabel(f"Daily closing prices ({self.config['pair']})")
        plt.plot(times, dailyClose,
                 label=f"{self.config['pair']} close price", color="black")
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
            f"EMA {LONG_EMA_LEN}/{SHORT_EMA_LEN} Day Cross with Buy and Sell Indicators for {self.config['pair']} ({days} days)")
        plt.show()

    def run(self) -> None:
        # initialize state with past year of data
        days = 365
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
        for dayIdx in range(LONG_EMA_LEN, days):
            closePrice = float(daily[dayIdx][OHLC.close])
            shortEMA = (shortEMA * (1 - shortSmoothing) +
                        (closePrice * shortSmoothing))
            longEMA = (longEMA * (1 - longSmoothing) +
                       (closePrice * longSmoothing))

        self.state = {
            'longEMA': longEMA,
            'shortEMA': shortEMA,
            'bought': False
        }
        schedule.every(10).seconds.do(self._analyze)
        # schedule.every().day.at("18:00").do(self._analyze)
        while True:
            schedule.run_pending()
            time.sleep(1)
