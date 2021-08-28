from typing import *
from decimal import Decimal
from datetime import datetime as dt, date, timedelta
import time

import schedule
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import cbpro

from src.constants import *


class NeilBot():
    def __init__(self, config: Dict, publicClient: cbpro.PublicClient, authClient: cbpro.AuthenticatedClient):
        """Inits NeilBot with an API client and coin-currency pair"""
        self.config = config
        self.publicClient = publicClient
        self.authClient = authClient
        self.state = {
            "longEMA": 0,
            "shortEMA": 0,
            "bought": False,
            "buyPrice": 0,
            "crossCount": 0
        }

    def _sendEmail(self):
        # TODO: implement email notifications
        pass

    def _buy(self, amount) -> None:
        """ Buy
        """
        response = self.authClient.place_market_order(size=amount,
                                                      side='buy',
                                                      product_id=self.config['pair'])
        return response

    def _sell(self, amount) -> None:
        """ Sell
        """
        response = self.authClient.place_market_order(
            size=amount,
            side='sell',
            product_id=self.config['pair'])
        return response

    def _analyze(self) -> None:
        """
        Analyze for the occurrence of a buy or sell signal for today
        """
        pastDay = self.publicClient.get_product_24hr_stats(
            'ETH-USD')  # past day OHLC

        # query for latest day ohlc
        longSmoothing = SMOOTHING_FACTOR / (1 + self.config["longEMALen"])
        shortSmoothing = SMOOTHING_FACTOR / (1 + SHORT_EMA_LEN)

        prevShortEMA = self.state["shortEMA"]
        prevLongEMA = self.state["longEMA"]

        # compute EMA's
        closePrice = float(pastDay["last"])
        curShortEMA = (self.state['shortEMA'] * (1 - shortSmoothing) +
                       (closePrice * shortSmoothing))
        curLongEMA = (self.state['longEMA'] * (1 - longSmoothing) +
                      (closePrice * longSmoothing))

        # count amount of times a cross has occurred
        if (prevShortEMA < prevLongEMA and curLongEMA < curShortEMA) \
                or (prevLongEMA < prevShortEMA and curShortEMA < curLongEMA):
            self.state['crossCount'] += 1

        # wait for 2 crosses before taking a position
        if self.state['crossCount'] < 2:
            return

        # check for buy signal
        if not self.state['bought'] and curLongEMA < curShortEMA:
            usdc_account = self.authClient.get_account(
                self.config["USDC_account"])
            available_usdc = "{:.8f}".format(float(usdc_account["available"]))
            self._buy(available_usdc)

        # sell signal or stop loss at 10%
        elif self.state['bought'] and ((curShortEMA < curLongEMA or (closePrice < 0.9 * self.state['buyPrice']))):
            eth_account = self.authClient.get_account(
                self.config["ETH_account"])
            available_eth = "{:.8f}".format(float(eth_account["available"]))
            self._sell(available_eth)

    def _queryOHLC(self, days) -> List[List[OHLC]]:
        """get OHLC data in the period of number of days from now
        """
        today = dt.utcnow().today()
        end = today.date()

        t_delta = timedelta(days=days-1)

        start = today - t_delta
        start = start.date()

        daily = self.publicClient.get_product_historic_rates(
            self.config["pair"], granularity=86400, start=start, end=end)
        daily.reverse()
        return daily

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

    def plot(self, days) -> None:
        """plot the long and short EMA's on an OHLC candlestick mpl plot

        :param days: number of days to backtest over from today
        :type days: int
        """
        results = self.backtest(days)
        daily = self._queryOHLC(days)
        dailyClose = np.array([float(dayOHLC[OHLC.close])
                               for dayOHLC in daily])

        times = np.array([dt.utcfromtimestamp(dayOHLC[OHLC.time]).strftime('%b %d %y %H:%M')
                          for dayOHLC in daily])

        fig, ax = plt.subplots()

        plt.xlabel('Dates (UTC)')
        plt.ylabel(f"Daily closing prices ({self.config['pair']})")
        plt.plot(times, dailyClose,
                 label=f"{self.config['pair']} close price", color="black")
        plt.plot(times, results['longEMAVals'],
                 label=f"{self.config['longEMALen']} EMA", color="blue")
        plt.plot(times, results['shortEMAVals'],
                 label=f"{self.config['shortEMALen']} EMA", color="orange")
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
            f"EMA {self.config['longEMALen']}/{self.config['shortEMALen']} Day Cross with Buy and Sell Indicators for {self.config['pair']} ({days} days)")
        plt.show()

    def run(self) -> None:
        # initialize state with past 300 days of data
        days = 300
        daily = self._queryOHLC(days)
        dailyClose = np.array([float(dayOHLC[OHLC.close])
                               for dayOHLC in daily])

        # compute initial long and short EMA ie. the respective SMA's
        longEMA = sum(dailyClose[:self.config["longEMALen"]]
                      ) / self.config["longEMALen"]
        shortEMA = sum(
            dailyClose[SHORT_EMA_LEN: self.config["longEMALen"]]) / (self.config["longEMALen"] - SHORT_EMA_LEN)
        longSmoothing = SMOOTHING_FACTOR / (1 + self.config["longEMALen"])
        shortSmoothing = SMOOTHING_FACTOR / (1 + SHORT_EMA_LEN)
        for dayIdx in range(self.config["longEMALen"], days):
            closePrice = float(daily[dayIdx][OHLC.close])
            shortEMA = (shortEMA * (1 - shortSmoothing) +
                        (closePrice * shortSmoothing))
            longEMA = (longEMA * (1 - longSmoothing) +
                       (closePrice * longSmoothing))

        self.state = {
            "longEMA": longEMA,
            "shortEMA": shortEMA,
            "bought": False,
            "buyPrice": 0,
            "crossCount": 0
        }

        while True:
            cur_time = dt.utcnow().strftime("%H")
            print('hi')
            if cur_time == "23":
                self._analyze()
            time.sleep(TWENTY_FOUR_HOURS)
