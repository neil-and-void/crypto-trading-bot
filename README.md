# Ethereum Crypto Trading Bot
Ethereum trading bot using an EMA 10-5 day cross indicator. Also provides backtesting and plotting functionality.

# Technologies Used
* Python
* Numpy
* Pandas
* MatPlotLib
* Kraken API
* Docker

# Setup
* clone repo
* initialize python virtual environment `python3 -m venv env`
* install dependencies `pip install -r requirements.txt```
* Sign up for Kraken API and copy API key and secret to .env as outlined in sample.env
* start venv `source env/bin/activate`

# Running
`python app.py <COMMAND>`

# Commands
* `help` list commands
* `test` run a backtest
* `plot` plot the strategies and it's performance on an MPL plot
* `start` run the strategy live

# Backtesting results
## 3 months from June 19
* profits: $72.155
* profit (%): 72.155%
![3 month backtest plot](./images/backtest_3month.png "3 month backtest plot")
## 1 year from June 19
* profits: $719.138
* profit (%): 719.138%
![1 Year backtest plot ](./images/backtest_1year.png "1 year backtest plot")

# Disclaimer
If you want to use this bot, you are using it at your own risk. I'm not responsible for any money lost.