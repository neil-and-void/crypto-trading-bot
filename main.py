import sys
import getopt
import time
from decimal import Decimal

from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.error import ClientError
from src.backtester import Backtester
from src.plotter import Plotter
from src.binance_client import Binance
from src import config
from src.constants import *
from src.bot import NeilBot


if __name__ == "__main__":
    optlist, _ = getopt.getopt(sys.argv[1:], 'b:h:r')
    binance = Binance(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)
    neil_bot = NeilBot(
        long_smoothing=config.LONG_EMA_SMOOTHING,
        long_ema_period=config.LONG_EMA_PERIOD,
        short_smoothing=config.SHORT_EMA_SMOOTHING,
        short_ema_period=config.SHORT_EMA_PERIOD,
        rsi_period=config.RSI_PERIOD,
        rsi_threshold=config.RSI_THRESHOLD)

    for opt, arg in optlist:
        if opt in ("-h"):
            print("Examples of Usage:")
            print("Print backtest results for past 90 periods: main.py --backtest 90")
            print(
                "Generate backtest results on MPL plot for 90 periods: main.py --backtest 90")

        elif opt in ('-b'):
            period_length = int(arg)
            min_initialization_length = max(config.LONG_EMA_PERIOD,
                                            config.SHORT_EMA_PERIOD, config.RSI_PERIOD)
            if period_length <= min_initialization_length:
                print(
                    'period length needs to be greater than minimum initialization length')
                exit(1)

            ohlc = binance.get_ohlc(
                config.COIN_PAIR, Client.KLINE_INTERVAL_1HOUR, limit=period_length)
            backtester = Backtester()
            buys, sells = backtester.backtest(
                ohlc, neil_bot, min_initialization_length)

            plotter = Plotter()
            plotter.generate_plot(
                ohlc[min_initialization_length:], buys, sells, config.COIN_PAIR, period_length, Client.KLINE_INTERVAL_1HOUR)

        elif opt in ('-r'):
            # fetch as many periods as the longest period for indicators
            initial_length = max(config.LONG_EMA_PERIOD,
                                 config.SHORT_EMA_PERIOD, config.RSI_PERIOD)
            ohlc_data = binance.get_ohlc(
                config.COIN_PAIR, Client.KLINE_INTERVAL_1HOUR, limit=initial_length)
            neil_bot.initialize_values(ohlc_data)

            while True:
                ohlc = binance.get_ohlc(
                    config.COIN_PAIR, Client.KLINE_INTERVAL_1HOUR, limit=1)[0]
                signal = neil_bot.analyze(ohlc)
                try:
                    if signal == BUY:
                        # buy as much base currency with quote as we can
                        busd_balance = binance.get_coin_balance('BUSD', 10000)
                        binance.buy(Decimal(busd_balance), config.COIN_PAIR)
                        print(f'$$$ BUY SIGNAL: ${ohlc[CLOSE]} $$$')

                    elif signal == SELL:
                        # sell as much quote currency currency as we can
                        eth_balance = binance.get_coin_balance('ETH', 10000)
                        busd_quantity = float(eth_balance) * float(ohlc[CLOSE])
                        binance.sell(round(busd_quantity, 6), config.COIN_PAIR)
                        print(f'$$$ SELL SIGNAL: ${ohlc[CLOSE]} $$$')

                except (BinanceAPIException, ClientError) as e:
                    order_type = 'sell' if signal == SELL else 'buy'
                    print(
                        f'### Failed attempt to place a {order_type} order.###\n Error: {e}')

                except Exception as e:
                    print(e)

                time.sleep(config.PERIOD_LENGTH)

    exit()
