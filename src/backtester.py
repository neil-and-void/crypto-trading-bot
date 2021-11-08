from src import constants


class Backtester:
    def __init__(self, **kwargs):
        self.wallet = kwargs['wallet']
        self.coin_qty = kwargs['coin_qty']

    def backtest(self, ohlc_data, bot):
        buys = []
        sells = []

        bot.initialize_values(ohlc_data)

        for ohlc in ohlc_data:
            indicator = bot.analyze(ohlc)
            if indicator == constants.BUY:
                buys.append(ohlc[constants.CLOSE])
                sells.append(None)
            elif indicator == constants.SELL:
                buys.append(None)
                sells.append(ohlc[constants.CLOSE])
        return buys, sells

    def print_results(self, buys, sells, ohlc_data):
        pass
