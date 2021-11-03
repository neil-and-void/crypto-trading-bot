import sys
from datetime import datetime as dt, date, timedelta
from binance_client import Binance
import config

# import bot as NeilBot


if __name__ == "__main__":
    binance = Binance(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)
    binance.get_wallet(dt.now().timestamp())
    binance.get_account()

    cmd = sys.argv[1]
    if len(sys.argv) <= 1:
        print("Must pass command to bot.")

    if cmd == "help":
        pass

    elif cmd == "test":
        pass

    elif cmd == "plot":
        pass

    elif cmd == "run":
        while True:
            pass

    else:
        print("Invalid command, pass help to get more info")
