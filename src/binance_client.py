from binance.spot import Spot


class Binance:
    def __init__(self, api_key, secret_key):
        self.client = Spot(key=api_key, secret=secret_key)

    def buy(self):
        pass

    def sell(self):
        pass

    def get_ohlc(self):
        pass

    def get_wallet(self, timestamp):
        return self.client.coin_info(timestamp=timestamp)

    def get_account(self):
        return self.client.account()
