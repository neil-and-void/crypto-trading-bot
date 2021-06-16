from .strategy import Strategy
from typing import *
import sched
import time
from datetime import datetime, date, timedelta
import requests
import urllib.parse
import hashlib
import hmac
import json
import base64

import matplotlib.pyplot as plt
import numpy as np
from src.constants import *
import os
from os.path import join, dirname
from dotenv import load_dotenv




class NeilBot():
    def __init__(self, strategy: Strategy, fund=0, ethQty=0):
        self.strategy = strategy
        self.funds = funds
        self.ethQty = ethQty

    def _buy(self) -> None:
        pass

    def _sell(self) -> None:
        pass

    def evaluate(self) -> None:
        if self.strategy.evaluate():
            pass
            # check for sell off limit

            # check for buy signal

            # check for sell signal
        pass
