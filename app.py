import sys
from os.path import join, dirname
import os
from datetime import datetime as dt, date, timedelta
from dotenv import load_dotenv
import cbpro

from src.bot import NeilBot
from src.constants import *

dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path)
COINBASE_API_KEY = os.environ.get("COINBASE_API_KEY")
COINBASE_BASE_64_SECRET = os.environ.get("COINBASE_BASE_64_SECRET")
COINBASE_PASSPHRASE = os.environ.get("COINBASE_PASSPHRASE")


def main():
    commands = {"test", "plot", "run"}
    if len(sys.argv) <= 1 or sys.argv[1] not in commands:
        print("Invalid argument. Pass 'help' as the first argument when running app.py to get more info")
        return

    # Feel free to play with these values #
    config = {
        "pair": "ETH-USD",
        "smoothingFactor": 2,
        "shortEMALen": 5,
        "longEMALen": 13
    }
    publicClient = cbpro.PublicClient()
    authenticatedClient = cbpro.AuthenticatedClient(
        COINBASE_API_KEY, COINBASE_BASE_64_SECRET, COINBASE_PASSPHRASE, api_url="https://api-public.sandbox.pro.coinbase.com")
    # init api and bot
    neilBot = NeilBot(config, publicClient, authenticatedClient)

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
