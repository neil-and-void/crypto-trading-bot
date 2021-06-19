import sys
from os.path import join, dirname
import os
from datetime import datetime, date, timedelta

from dotenv import load_dotenv

from src.bot import NeilBot
import krakenex

dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path)
KRAKEN_PRIVATE_KEY = os.environ.get("KRAKEN_PRIVATE_KEY")
KRAKEN_API_KEY = os.environ.get("KRAKEN_API_KEY")


def main():
    commands = {"test", "plot", "start"}
    if len(sys.argv) <= 1 or sys.argv[1] not in commands:
        print("Invalid argument. Pass 'help' as the first argument when running app.py to get more info")
        return

    # init api and bot
    krakenexAPI = krakenex.API(key=KRAKEN_API_KEY, secret=KRAKEN_PRIVATE_KEY)
    pair = "XETHZUSD"  # TODO: change hardcoded pair
    neilBot = NeilBot(krakenexAPI, pair)

    arg = sys.argv[1]
    if arg == "help":
        print("""'test' - run strategy with past 3 months of closing prices\n'plot' - plot strategy for past 3 months\n'start' - run the strategy live""")

    elif arg == "test":
        results = neilBot.backtest(720)  # TODO: change hardcoded hours

    elif arg == "plot":
        neilBot.plot(720)  # TODO: change hardcoded hours

    elif arg == "start":
        neilBot.run()


if __name__ == "__main__":
    main()
