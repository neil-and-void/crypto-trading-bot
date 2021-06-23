import cbpro


class MockPublicClient(cbpro.PublicClient):
    def __init__(self):
        super().__init__()

    def get_product_historic_rates(self, product_id, start=None, end=None,
                                   granularity=None):
        return [
            [1415398768, 0.32, 4.2, 0.35, 4.2, 12.3],
        ]


class MockAuthenticatedClient(cbpro.AuthenticatedClient):
    def __init__(self, key, b64secret, passphrase, **kwargs):
        super().__init__(key, b64secret, passphrase, **kwargs)
