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
import pandas as pd
import os
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
KRAKEN_API_SEC = os.environ.get("KRAKEN_API_SEC")

##### GENERATED FROM KRAKEN DOCS #####


def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


data = {
    "nonce": "1616492376594",
    "ordertype": "limit",
    "pair": "XBTUSD",
    "price": 37500,
    "type": "buy",
    "volume": 1.25
}

signature = get_kraken_signature("/0/private/AddOrder", data, KRAKEN_API_SEC)


##### END OF GENERATED CODE #####

# get daily closing prices from last 3 months
pair = 'ETHCAD'
interval = 1440  # 1 day in minutes
today = datetime.today()
threeMonthDelta = timedelta(days=90)
threeMonthDateTime = today - threeMonthDelta
threeMonthDateTimeMilliseconds = int(threeMonthDateTime.timestamp() * 1000)
url = f'https://api.kraken.com/0/public/OHLC?pair={pair}&interval={interval}&since={1548111600}'
headers = {'API-Key': KRAKEN_API_SEC, 'API-Sign': signature}
# res = requests.get(url, headers=headers)

# get data for processing
f = open("data.txt", "r")
json_data = json.loads(f.read())
dailyClosingPrices = json_data['result']['XETHZCAD']
n = len(dailyClosingPrices)
longSum = 0
longMALen = 12
longLeft = 0
longRight = longMALen - 1

shortSum = 0
shortMALen = 6
shortLeft = longMALen - shortMALen - 1
shortRight = longMALen - 1

# get initial sums for the moving averages
dayIdx = 0
for dayIdx in range(longMALen):
    longSum += float(dailyClosingPrices[dayIdx][4])
    if shortMALen - 1 < dayIdx:
        shortSum += float(dailyClosingPrices[dayIdx][4])

# backtest over historical data
cost = 100
bought = False
while dayIdx < n - 1:
    # Buy signal
    if (longSum / longMALen) < (shortSum / shortMALen) and not bought:
        bought = True
        print('buy')
    # Sell signal
    if (shortSum / shortMALen) < (longSum / longMALen) and bought:
        bought = False
        print('sell')

    # slide short and longs windows over by 1 day
    dayIdx += 1
    longRight = shortRight = dayIdx

    shortSum += float(dailyClosingPrices[dayIdx][4]) - \
        float(dailyClosingPrices[shortLeft][4])
    shortLeft += 1

    longSum += float(dailyClosingPrices[dayIdx][4]) - \
        float(dailyClosingPrices[longLeft][4])
    longLeft += 1
