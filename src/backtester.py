from src.constants import *
import numpy as np


class Backtester:
    def backtest(self, ohlc_data, bot, min_initialization_length):
        """ Run backtest length amount of periods

        Args:
            ohlc_data (List): array of ohlc data to run bot against
            bot (NeilBot): Agent to run backtest with
            min_initialization_length (int): minimum length of ohlc data to fetch for initializing values in the bot

        Returns:
            Tuple[List, List]: Tuple of buy and sell prices the bot indicated signals for
        """
        buys = []
        sells = []

        bot.initialize_values(ohlc_data[:min_initialization_length])

        for ohlc in ohlc_data[min_initialization_length:]:
            signal = bot.analyze(ohlc)
            if signal == BUY:
                buys.append(float(ohlc[CLOSE]))
                sells.append(np.nan)
            elif signal == SELL:
                buys.append(np.nan)
                sells.append(float(ohlc[CLOSE]))
            else:
                sells.append(np.nan)
                buys.append(np.nan)
        return buys, sells
