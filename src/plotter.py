import numpy as np
import mplfinance as mpf
import pandas as pd

from src.constants import *


class Plotter:
    def generate_plot(self, ohlc_data, buys, sells, pair, length, interval):
        """ Plot buy and sell signals on ohlc data 

        Args:
            ohlc_data (List): List of ohlc data for the coin pari
            buys (List): Prices the bot indicated buy signals for
            sells (List): Prices the bot indicated sell signals for
            length (int): Number of intervals
            interval (String): Interval type
            pair (String): Coin pair 
        """
        ohlc_array = np.array(ohlc_data)

        # time
        close_times_df = pd.DataFrame(
            ohlc_array[:, CLOSE_TIME], columns=["CloseTimes"])

        # format ohlc data
        ohlc_df = pd.DataFrame(ohlc_array[:, [OPEN, HIGH, LOW, CLOSE]], columns=[
                               "Open", "High", "Low", "Close"])
        cols = ["Open", "High", "Low", "Close"]
        ohlc_df[cols] = ohlc_df[cols].apply(
            pd.to_numeric, errors='coerce', axis=1)
        ohlc_df = ohlc_df.join(close_times_df)
        ohlc_df = ohlc_df.set_index(pd.DatetimeIndex(
            pd.to_datetime(ohlc_df['CloseTimes'], unit='ms')))

        # setup buys dataframe
        buys_df = pd.DataFrame(buys, columns=["Buys"])
        sells_df = pd.DataFrame(sells, columns=["Sells"])
        bot_results_df = buys_df.join(sells_df)

        add_plot = mpf.make_addplot(bot_results_df, type='scatter', )

        mpf.plot(ohlc_df, type='candle',
                 addplot=add_plot, title=f'{pair} for {length} {interval} periods')
