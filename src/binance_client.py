from binance.spot import Spot
from binance.client import Client


class Binance:
    def __init__(self, api_key, secret_key):
        self.spot_client = Spot(key=api_key, secret=secret_key)
        self.client = Client(api_key, secret_key)

    def buy(self, quantity, symbol):
        return self.client.new_order({"type": "BUY", "symbol": symbol, "quantity": quantity, 'side': "MARKET"});

    def sell(self, quantity, symbol):
        return self.client.new_order({"type": "SELL", "symbol": symbol, "quantity": quantity, 'side': "MARKET"});

    def get_ohlc(self, symbol, interval, limit):
        return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

    def get_wallet(self, timestamp):
        return self.spot_client.coin_info(timestamp=timestamp)

    def get_account(self):
        return self.spot_client.account()

