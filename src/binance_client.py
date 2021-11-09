from binance.spot import Spot
from binance.client import Client


class Binance:
    def __init__(self, api_key, secret_key):
        self.spot_client = Spot(key=api_key, secret=secret_key)
        self.client = Client(api_key, secret_key)

    def buy(self, quantity, symbol):
        """ Issue a buy order for the coin with the given symbol

        :param quantity: [description]
        :param symbol: [description]
        :return: [description]
        """
        return self.spot_client.new_order(type="BUY", symbol=symbol, quantity=quantity, side="MARKET")

    def sell(self, quantity, symbol):
        """ Issue a buy order for the coin with the given symbol

        :param quantity: [description]
        :param symbol: [description]
        :return: [description]
        """
        return self.spot_client.new_order(type="SELL", symbol=symbol, quantity=quantity, side="MARKET")

    def get_ohlc(self, symbol, interval, limit):
        """ Get OHLC data about a coin in the given interval

        :param symbol: [description]
        :type symbol: [type]
        :param interval: [description]
        :type interval: [type]
        :param limit: [description]
        :type limit: [type]
        :return: [description]
        :rtype: [type]
        """
        return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

    def get_wallet(self, timestamp):
        return self.spot_client.coin_info(timestamp=timestamp)

    def get_account(self):
        return self.spot_client.account()
