from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from src import constants, config


class Plotter:
    def generate_plot(self, ohlc_data, buys, sells, pair):
        """ Plot buy and sell signals on ohlc data 

        Args:
            ohlc_data (List): List of ohlc data for the coin pari
            buys (List): Prices the bot indicated buy signals for
            sells (List): Prices the bot indicated sell signals for
            pair (String): Coin pair 
        """
        hourly_close = np.array([float(ohlc[constants.CLOSE])
                                 for ohlc in ohlc_data])

        times = np.array([dt.utcfromtimestamp(float(ohlc[constants.CLOSE_TIME])/1000).strftime('%b %d %y %H:%M')
                          for ohlc in ohlc_data])

        fig, ax = plt.subplots()

        plt.xlabel('Dates (UTC)')
        plt.ylabel(f"hourly closing prices ({config.COIN_PAIR})")
        plt.plot(times, hourly_close,
                 label=f"{pair} close price", color="black")
        plt.plot(times, buys, label="Buy Indicator", marker=".",
                 linestyle='None', color="green", markersize=10)
        plt.plot(times, sells, label="Sell Indicator", marker=".",
                 linestyle='None', color="red", markersize=10)

        plt.legend()
        ax.xaxis.set_major_locator(
            ticker.MultipleLocator(len(ohlc_data) // 12))
        plt.grid()
        fig.autofmt_xdate()
        ax.autoscale()
        plt.title(
            f"Buy and Sell Indicators for {pair}")
        plt.show()
