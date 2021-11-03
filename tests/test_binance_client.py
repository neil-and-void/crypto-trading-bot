from .. import config, binance_client


def test_smoke_binance_client():
    assert 1 + 1
    binance_client.Binance(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)
