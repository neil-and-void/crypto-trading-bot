import unittest
import os
from mock import patch
import cbpro
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime as dt, timedelta

from tests.mock_clients import MockPublicClient, MockAuthenticatedClient
from src.bot import NeilBot
from src.constants import *


dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path)
SANDBOX_COINBASE_API_KEY = os.environ.get("SANDBOX_COINBASE_API_KEY")
SANDBOX_COINBASE_BASE_64_SECRET = os.environ.get(
    "SANDBOX_COINBASE_BASE_64_SECRET")
SANDBOX_COINBASE_PASSPHRASE = os.environ.get("SANDBOX_COINBASE_PASSPHRASE")
SANDBOX_COINBASE_URL = os.environ.get("SANDBOX_COINBASE_URL")

# Mock OHLC data
buySignalData = {"last": 9000}
sellSignalData = {"last": 100}
stopLossSignalData = {"last": 10}


class TestNeilBotMethods(unittest.TestCase):
    def setUp(self):
        publicClient = cbpro.PublicClient()
        authenticatedClient = cbpro.AuthenticatedClient(
            SANDBOX_COINBASE_API_KEY, SANDBOX_COINBASE_BASE_64_SECRET, SANDBOX_COINBASE_PASSPHRASE, api_url=SANDBOX_COINBASE_URL)
        config = {
            "pair": "ETH-USD",
            "smoothingFactor": 2,
            "shortEMALen": 5,
            "longEMALen": 15
        }
        self.neilBot = NeilBot(config, publicClient, authenticatedClient)

    @patch.object(NeilBot, "_buy")
    @patch.object(cbpro.PublicClient, "get_product_24hr_stats", return_value=buySignalData)
    def test_buy_signal(self, mock_get_product_24hr_stats, mock_buy):
        """ Test that bot buys when bot receives data that indicates a buy signal

        :param mock_buy: [description]
        :type mock_buy: [type]
        :param mock_get_product_24hr_stats: [description]
        :type mock_get_product_24hr_stats: [type]
        """
        self.neilBot.state = {
            "longEMA": 5000,
            "shortEMA": 4999,
            "bought": False,
            "crossCount": 2,
            "buyPrice": 0
        }
        self.neilBot._analyze()
        self.assertTrue(mock_buy.called)

    @patch.object(NeilBot, "_sell")
    @patch.object(cbpro.PublicClient, "get_product_24hr_stats", return_value=sellSignalData)
    def test_sell_signal(self, mock_get_product_24hr_stats, mock_sell):
        """ Test that bot sells when bot receives data that indicates a sell signal
        """
        self.neilBot.state = {
            "longEMA": 4999,
            "shortEMA": 5000,
            "bought": True,
            "crossCount": 2,
            "buyPrice": 0
        }
        self.neilBot._analyze()
        self.assertTrue(mock_sell.called)

    @patch.object(NeilBot, "_sell", return_value=None)
    @patch.object(cbpro.PublicClient, "get_product_24hr_stats", return_value=sellSignalData)
    def test_stop_loss_signal(self, mock_get_product_24hr_stats, mock_sell):
        """ Test that bot sells when bot receives data that indicates a stop loss signal
        """
        self.neilBot.state = {
            "longEMA": 5000,
            "shortEMA": 2500,
            "bought": True,
            "crossCount": 2,
            "buyPrice": 4000
        }
        self.neilBot._analyze()
        self.assertTrue(mock_sell.called)

    def test_backtest(self):
        """ Smoke test backtesting
        """
        self.neilBot.backtest(200)

    # def test_plot(self):
    #     """ Smoke test plotting functionality
    #     """
    #     self.neilBot.plot(200)


if __name__ == '__main__':
    unittest.main()
