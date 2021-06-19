
from dotenv import load_dotenv
from os.path import join, dirname
import os
import csv
import numpy as np
import mplfinance as mpf
import pandas as pd
import matplotlib.dates as mpl_dates
import math
import matplotlib.pyplot as plt
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
from enum import IntEnum
from constants import *


dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)
KRAKEN_PRIVATE_KEY = os.environ.get("KRAKEN_PRIVATE_KEY")
KRAKEN_API_KEY = os.environ.get("KRAKEN_API_KEY")

krakenexAPI = api(key=KRAKEN_API_KEY, secret=KRAKEN_PRIVATE_KEY)


class OHLC_Data(IntEnum):
    time = 0
    open = 1
    high = 2
    low = 3
    close = 4
    vwap = 5
    volume = 6
    count = 7


##### GENERATED FROM KRAKEN DOCS #####


def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


# TODO: correct this
data = {
    "nonce": "1616492376594",
    "ordertype": "limit",
    "pair": "XBTUSD",
    "price": 37500,
    "type": "buy",
    "volume": 1.25
}

signature = get_kraken_signature(
    "/0/private/AddOrder", data, KRAKEN_PRIVATE_KEY)


##### END OF GENERATED CODE #####

# get daily closing prices from last 3 months
pair = 'ETHCAD'
interval = 1440  # 1 day in minutes
today = datetime.today()
threeMonthDelta = timedelta(days=90)
threeMonthDateTime = today - threeMonthDelta
threeMonthDateTimeMilliseconds = int(threeMonthDateTime.timestamp())

url = f'https://api.kraken.com/0/public/OHLC?pair={pair}&interval={interval}&since={threeMonthDateTimeMilliseconds}'
headers = {'API-Key': KRAKEN_PRIVATE_KEY, 'API-Sign': signature}
res = requests.get(url, headers=headers)
dailyOHLC = res.json()['result']['XETHZCAD']
# get daily closing prices from last 3 months
pair = 'ETHUSD'
interval = 1440  # 1 day in minutes
today = datetime.today()
threeMonthDelta = timedelta(days=90)
threeMonthDateTime = today - threeMonthDelta
threeMonthDateTimeMilliseconds = int(threeMonthDateTime.timestamp())

dailyOHLC = k.query_public(
    f'OHLC?pair={pair}&interval={interval}&since={threeMonthDateTimeMilliseconds}')


# write data to data.txt
# f = open("data.txt", "w")
# f.write(res.text)

# write data to data.csv
# with open('data.csv', 'w', newline='') as csvfile:
#     csvWriter = csv.writer(csvfile, delimiter=',',
#                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

#     csvWriter.writerow([label.name for label in OHLC_Data])
#     for day in dailyOHLC:
#         csvWriter.writerow(day)

# get data for processing
f = open("data.txt", "r")
json_data = json.loads(f.read())
dailyOHLC = json_data['result']['XETHZCAD']

# initialize variables for backtesting
timeFrameLen = len(dailyOHLC)

longEMA = 0
longSmoothingFactor = SMOOTHING_FACTOR / (1 + LONG_EMA_LEN)

shortEMA = 0
shortSmoothingFactor = SMOOTHING_FACTOR / (1 + SHORT_EMA_LEN)

# compute initial short and long SMA to use as initial previous EMA
for dayIdx in range(SHORT_EMA_LEN, LONG_EMA_LEN):
    shortEMA += float(dailyOHLC[dayIdx][OHLC_Data.close])
for dayIdx in range(LONG_EMA_LEN):
    longEMA += float(dailyOHLC[dayIdx][OHLC_Data.close])
shortEMA /= SHORT_EMA_LEN
longEMA /= LONG_EMA_LEN

# data for mplfinance plot
longEMAVals = [np.nan for i in range(LONG_EMA_LEN)]
shortEMAVals = [np.nan for i in range(LONG_EMA_LEN)]
sellVals = [np.nan for i in range(timeFrameLen)]
buyVals = [np.nan for i in range(timeFrameLen)]

# go through the rest of the days and compute EMA's
funds = originalFunds = 100
ethQty = 0
bought = False
dayIdx = LONG_EMA_LEN
closePrice = 0
buyPrice = 0
while dayIdx < timeFrameLen:
    closePrice = float(dailyOHLC[dayIdx][OHLC_Data.close])
    shortEMA = (shortEMA * (1 - shortSmoothingFactor) +
                (closePrice * shortSmoothingFactor))
    longEMA = (longEMA * (1 - longSmoothingFactor) +
               (closePrice * longSmoothingFactor))

    # TODO: stop loss
    # if bought and cllo:
    # buy signal
    if not bought and longEMA < shortEMA:
        ethQty = funds / closePrice
        buyVals[dayIdx] = closePrice
        buyPrice = closePrice
        bought = True
    # sell signal
    if bought and ((shortEMA < longEMA) or ((ethQty * closePrice) < 0.9 * (ethQty * buyPrice))):
        funds = ethQty * closePrice
        sellVals[dayIdx] = closePrice
        bought = False

    longEMAVals.append(longEMA)
    shortEMAVals.append(shortEMA)
    dayIdx += 1
    print(f'{closePrice} | {longEMA} | {shortEMA}')

# convert owned Ethereum to cash
if bought:
    funds = ethQty * closePrice

# outcome of strategy
print(f'Funds: {funds} | Profit {funds - originalFunds}')


def dateparse(unixTime):
    return datetime.fromtimestamp(float(unixTime))


# plot EMA, buy and sell vals on OHLC plot
daily = pd.read_csv('data.csv', index_col=0, parse_dates=[
                    0], date_parser=dateparse)
daily.index.name = 'Date'
ap = [
    mpf.make_addplot(longEMAVals, color='blue', type='line'),
    mpf.make_addplot(shortEMAVals, color='orange', type='line'),
    mpf.make_addplot(sellVals, color='red', type='scatter', markersize=75),
    mpf.make_addplot(buyVals, color='green', type='scatter', markersize=75)
]
mpf.plot(daily, type='candle', show_nontrading=True,
         style='ibd', addplot=ap)
