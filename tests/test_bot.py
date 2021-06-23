import unittest
import os
import cbpro
from os.path import join, dirname
from dotenv import load_dotenv
from datetime import datetime as dt, timedelta

from tests.mock_clients import MockPublicClient, MockAuthenticatedClient
from src.bot import NeilBot
from src.constants import *


dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path)
COINBASE_API_KEY = os.environ.get("COINBASE_API_KEY")
COINBASE_BASE_64_SECRET = os.environ.get("COINBASE_BASE_64_SECRET")
COINBASE_PASSPHRASE = os.environ.get("COINBASE_PASSPHRASE")


class TestNeilBotMethods(unittest.TestCase):
    def setUp(self):
        # publicClient = MockPublicClient()
        # authenticatedClient = MockAuthenticatedClient(
        #     COINBASE_API_KEY, COINBASE_BASE_64_SECRET, COINBASE_PASSPHRASE)
        publicClient = cbpro.PublicClient()
        authenticatedClient = cbpro.AuthenticatedClient(
            COINBASE_API_KEY, COINBASE_BASE_64_SECRET, COINBASE_PASSPHRASE, api_url="https://api-public.sandbox.pro.coinbase.com")
        config = {
            "pair": "ETH-USD",
            "smoothingFactor": 2,
            "shortEMALen": 5,
            "longEMALen": 15
        }
        self.neilBot = NeilBot(config, publicClient, authenticatedClient)

    def test_query_OHLC(self):
        today = dt.utcnow().today()
        end = today.date()

        t_delta = timedelta(days=200)

        start = today - t_delta
        start = start.date()

        print(start, end)

        res = self.neilBot._queryOHLC(start, end)

        print(res)


if __name__ == '__main__':
    unittest.main()
