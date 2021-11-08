from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from src import constants, config


class Plotter:
    def generate_plot(self, ohlc_data, buys, sells):
        """plot the long and short EMA's on an OHLC candlestick mpl plot

        :param days: number of days to backtest over from today
        :type days: int
        """
        hourly_close = np.array([float(ohlc[constants.CLOSE])
                                 for ohlc in ohlc_data])

        times = np.array([dt.utcfromtimestamp(ohlc[constants.CLOSE_TIME]).strftime('%b %d %y %H:%M')
                          for ohlc in ohlc_data])

        fig, ax = plt.subplots()

        plt.xlabel('Dates (UTC)')
        plt.ylabel(f"hourly closing prices ({config.COIN_PAIR})")
        plt.plot(times, hourly_close,
                 label=f"{self.config['pair']} close price", color="black")
        plt.plot(times, buys,
                 label="Buy Indicator", marker=".", linestyle='None', color="green", markersize=10)
        plt.plot(times, sells,
                 label="Sell Indicator", marker=".", linestyle='None', color="red", markersize=10)

        plt.legend()
        ax.xaxis.set_major_locator(
            ticker.MultipleLocator(len(ohlc_data) // 12))
        plt.grid()
        fig.autofmt_xdate()
        ax.autoscale()
        plt.title(
            f"{config.EMA_PERIOD}-EMA and {config.RSI_PERIOD} period RSI lookback with Buy and Sell Indicators for {self.config['pair']}")
        plt.show()
