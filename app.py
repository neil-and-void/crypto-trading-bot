import sys
from os.path import join, dirname
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

from src.bot import NeilBot
from src.constants import *
import krakenex

dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path)
KRAKEN_PRIVATE_KEY = os.environ.get("KRAKEN_PRIVATE_KEY")
KRAKEN_API_KEY = os.environ.get("KRAKEN_API_KEY")


def main():
    commands = {"test", "plot", "run"}
    if len(sys.argv) <= 1 or sys.argv[1] not in commands:
        print("Invalid argument. Pass 'help' as the first argument when running app.py to get more info")
        return

    # init api and bot
    krakenexAPI = krakenex.API(key=KRAKEN_API_KEY, secret=KRAKEN_PRIVATE_KEY)
    config = {
        "pair": "XETHZUSD",
        "longSmoothing": "",
        "shortSmoothing": "",
        "shortEMALen": 5,
        "longEMALen": 15
    }
    pair = "XETHZUSD"  # TODO: change hardcoded pair
    neilBot = NeilBot(krakenexAPI, pair)

    arg = sys.argv[1]
    days = int(sys.argv[2])

    if arg == "help":
        print("""'test' - run strategy with past 3 months of closing prices\n'plot' - plot strategy for past 3 months\n'start' - run the strategy live""")

    elif arg == "test":
        results = neilBot.backtest(days)  # TODO: change hardcoded hours
        profits = results['wallet'] - results['initialWallet']
        percentage = profits / results['initialWallet']
        print('=== from {days} days ago to today ===\nprofits: {profits:.3f}\nprofit (%): {percentage:.3%}'.format(days=days,
                                                                                                                   profits=profits, percentage=percentage))

    elif arg == "plot":
        neilBot.plot(days)  # TODO: change hardcoded hours

    elif arg == "run":
        neilBot.run()


if __name__ == "__main__":
    main()
