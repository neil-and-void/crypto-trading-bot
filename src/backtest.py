
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
KRAKEN_API_SEC = os.environ.get("KRAKEN_API_SEC")


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

signature = get_kraken_signature("/0/private/AddOrder", data, KRAKEN_API_SEC)


##### END OF GENERATED CODE #####

# get daily closing prices from last 3 months
pair = 'ETHCAD'
interval = 1440  # 1 day in minutes
today = datetime.today()
threeMonthDelta = timedelta(days=90)
threeMonthDateTime = today - threeMonthDelta
threeMonthDateTimeMilliseconds = int(threeMonthDateTime.timestamp())

url = f'https://api.kraken.com/0/public/OHLC?pair={pair}&interval={interval}&since={threeMonthDateTimeMilliseconds}'
headers = {'API-Key': KRAKEN_API_SEC, 'API-Sign': signature}
res = requests.get(url, headers=headers)
dailyOHLC = res.json()['result']['XETHZCAD']

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

# backtest over historical data

# initialize matplotlib plot


# initialize variables for backtesting
timeFrameLen = len(dailyOHLC)

longEMA = 0
prevLongEMA = 0
longLeft = 0
longRight = LONG_EMA_LEN - 1
longSmoothingFactor = SMOOTHING_FACTOR / (1 + LONG_EMA_LEN)

shortEMA = 0
prevShortEMA = 0
shortLeft = LONG_EMA_LEN - SHORT_EMA_LEN - 1
shortRight = LONG_EMA_LEN - 1
shortSmoothingFactor = SMOOTHING_FACTOR / (1 + SHORT_EMA_LEN)

# compute initial short and long EMA's
longEMAVals = []
shortEMAVals = [np.nan for i in range(SHORT_EMA_LEN)]

dayIdx = 0
for dayIdx in range(LONG_EMA_LEN):
    # compute long EMA
    longEMA += (prevLongEMA * (1 - longSmoothingFactor)) + \
        (float(dailyOHLC[dayIdx][OHLC_Data.close]) * longSmoothingFactor)
    prevLongEMA = longEMA

    # compute short EMA
    if (SHORT_EMA_LEN - 1) < dayIdx:
        shortEMA += (prevShortEMA * (1 - shortSmoothingFactor)) + \
            (float(dailyOHLC[dayIdx][OHLC_Data.close]) * shortSmoothingFactor)
        prevShortEMA = shortEMA
        shortEMAVals.append(shortEMA)
    longEMAVals.append(longEMA)

funds = originalFunds = 100
ethQty = 0
bought = False
dayIdx += 1
while dayIdx < timeFrameLen:
    longEMA -= (float(dailyOHLC[dayIdx - LONG_EMA_LEN]
                [OHLC_Data.close]) * longSmoothingFactor)
    longEMA = (longEMA * (1 - longSmoothingFactor) +
               (float(dailyOHLC[dayIdx][OHLC_Data.close]) * longSmoothingFactor))

    shortEMA -= (float(dailyOHLC[dayIdx - SHORT_EMA_LEN]
                 [OHLC_Data.close]) * shortSmoothingFactor)
    shortEMA = (shortEMA * (1 - shortSmoothingFactor) +
                (float(dailyOHLC[dayIdx][OHLC_Data.close]) * shortSmoothingFactor))

    longEMAVals.append(longEMA)
    shortEMAVals.append(shortEMA)
    # print(
    #     f'{float(dailyOHLC[dayIdx][OHLC_Data.close])} | {longEMA} | {shortEMA}')
    dayIdx += 1

# outcome of strategy
# if bought:
#     funds = ethQty * curClosingPrice
# print(f'Funds: {funds} | Profit {funds - originalFunds}')


def dateparse(unixTime):
    return datetime.fromtimestamp(float(unixTime))


daily = pd.read_csv('data.csv', index_col=0, parse_dates=[
                    0], date_parser=dateparse)
daily.index.name = 'Date'

ap = [
    mpf.make_addplot(longEMAVals, color='blue', type='line'),
    mpf.make_addplot(shortEMAVals, color='orange', type='line')
]
fig, ax = mpf.plot(daily, type='hollow_and_filled',
                   style='yahoo', addplot=ap)

ax[0].legend(['hi'])
