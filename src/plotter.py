from datetime import datetime as dt, date, timedelta

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


class Plotter:
    def __init__(self, **kwargs):
        self.bot = kwargs.get('bot', None)

    def generate_plot(self):
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
