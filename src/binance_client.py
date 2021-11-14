from binance.spot import Spot
from binance.enums import *
from binance.client import Client


class Binance:
    def __init__(self, api_key, secret_key):
        """ initialize Binance class with Spot and Binance Clients given the api and secret keys

        Args:
            api_key (str): Binance API key
            secret_key (str): Binance API secret key
        """
        self.spot_client = Spot(key=api_key, secret=secret_key)
        self.client = Client(api_key, secret_key)

    def buy(self, quantity, symbol, timestamp):
        """ Issue a buy order

        Args:
            quantity (Decimal): Amount of quote currency to buy
            symbol (String): Coin symbol
            timestamp (int): Unix timestamp of Binance server for synchronization purposes

        Returns:
            dict: Response data of buy order
        """
        return self.client.create_order(side=SIDE_BUY, symbol=symbol, quoteOrderQty=quantity, type=ORDER_TYPE_MARKET, timestamp=timestamp)

    def sell(self, quantity, symbol, timestamp):
        """ Issue a sell order

        Args:
            quantity (Decimal): Amount of base currency to sell
            symbol (String): Coin symbol
            timestamp (int): Unix timestamp of Binance server for synchronization purposes

        Returns:
            dict: Response data of sell order
        """
        return self.spot_client.new_order(side=SIDE_SELL, symbol=symbol, quoteOrderQty=quantity, type=ORDER_TYPE_MARKET, timestamp=timestamp)

    def get_ohlc(self, symbol, interval, limit):
        """ Get ohlc data for coin in the given interval

        Args:
            symbol (String): Coin symbol
            interval (String): Interval length given by Binance constants
            limit (int): Number of ohlc data to limit response to

        Returns:
            [type]: [description]
        """
        return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

    def get_coin_balance(self, symbol, timestamp):
        """ Get balance of coin in wallet

        Args:
            symbol (String): Coin symbol
            timestamp (int): Unix timestamp of Binance server for synchronization purposes

        Returns:
            String : Quantity of coin in wallet
        """
        coins = self.spot_client.coin_info(timestamp=timestamp)
        for coin in coins:
            if coin['coin'] == symbol:
                return coin['free']

    def get_server_time(self):
        """ Get the current Binance server time

        Returns:
            int: Unix timestamp of Binance server
        """
        return self.client.get_server_time()['serverTime']
