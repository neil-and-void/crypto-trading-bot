from src import constants


class Backtester:
    def __init__(self, **kwargs):
        """ Initialize backtester with values for wallet and coin_qty to run backtest with
        """
        self.wallet = kwargs['wallet']
        self.coin_qty = kwargs['coin_qty']

    def backtest(self, ohlc_data, bot, length):
        """ Run backtest length amount of periods

        :param ohlc_data: [description]
        :type ohlc_data: [type]
        :param bot: [description]
        :type bot: [type]
        :return: [description]
        :rtype: [type]
        """
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

    def print_results(self, hi):
        print(self.wallet, self.coin_qty)
