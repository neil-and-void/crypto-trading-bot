import sys
from datetime import datetime as dt, date, timedelta
from binance.client import Client
import getopt

from src.backtester import Backtester
from src.plotter import Plotter
from src.binance_client import Binance
from src import config
from src.bot import NeilBot


if __name__ == "__main__":
    binance = Binance(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)
    neil_bot = NeilBot(smoothing=config.SMOOTHING_FACTOR,
                       ema_period=config.EMA_PERIOD,
                       rsi_period=config.RSI_PERIOD)

    optlist, _ = getopt.getopt(sys.argv[1:], 'b:p:h:', [
                               'backtest', 'plot', 'help'])

    plot = False
    for opt, _ in optlist:
        if opt == '--backtest':
            backtester = Backtester(wallet=200, coin_qty=0)
            ohlc = binance.get_ohlc(
                'ETHUSDT', Client.KLINE_INTERVAL_1HOUR, limit=100)
            buys, sells = backtester.backtest(ohlc, neil_bot)
            if opt == '--plots':
                plotter = Plotter()
                plotter.generate_plot(ohlc, buys, sells)

        elif opt in ("-help"):
            print("Examples of Usage:")
            print("Print backtest results: main.py --backtest")
            print(
                "Generate backtest results on MPL plot: main.py --backtest --plot")
            exit()
