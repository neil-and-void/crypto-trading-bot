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
    optlist, _ = getopt.getopt(sys.argv[1:], 'b:p:h:', [
                               'backtest', 'plot', 'help', 'period'])
    binance = Binance(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)
    neil_bot = NeilBot(
        long_smoothing=config.LONG_EMA_SMOOTHING,
        long_ema_period=config.LONG_EMA_PERIOD,
        short_smoothing=config.SHORT_EMA_SMOOTHING,
        short_ema_period=config.SHORT_EMA_PERIOD,
        rsi_period=config.RSI_PERIOD,
        rsi_threshold=config.RSI_THRESHOLD)

    plot = False
    buys = []
    sells = []
    for opt, arg in optlist:
        print(opt)
        if opt in ('--backtest'):
            backtester = Backtester(wallet=200, coin_qty=0)
            ohlc = binance.get_ohlc(
                'ETHUSDT', Client.KLINE_INTERVAL_1HOUR, limit=100)
            buys, sells = backtester.backtest(ohlc, neil_bot, arg)
            plotter = Plotter()
            plotter.generate_plot(ohlc, buys, sells)

        elif opt in ('--plot'):
            print('hi')
            plot = True
        elif opt in ("--help"):
            print("Examples of Usage:")
            print("Print backtest results for past 90 periods: main.py --backtest 90")
            print(
                "Generate backtest results on MPL plot for 90 periods: main.py --backtest 90 --plot")

    exit()
