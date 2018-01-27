from collections import defaultdict
from models.coin_model import Coin
class AcxExchange:
    class Market:
        BITCOIN = "btcaud"
        ETHER = "ethaud"
        HSR = "hsraud"
        BCH = "bchaud"

    def __init__(self):
        self.coins ={
            AcxExchange.Market.BITCOIN: Coin( AcxExchange.Market.BITCOIN),
            AcxExchange.Market.ETHER : Coin(AcxExchange.Market.ETHER),
            AcxExchange.Market.HSR: Coin(AcxExchange.Market.HSR),
            AcxExchange.Market.BCH: Coin(AcxExchange.Market.BCH)
        }


class GdxExchange:
    class Market:
        BITCOIN = 'BTC-USD'
        ETHER = 'ETH-USD'
        LTC =  'LTC-USD'
        BCH = 'BCH-USD'

    def __init__(self):
        self.coins ={
            GdxExchange.Market.BITCOIN: Coin( GdxExchange.Market.BITCOIN),
            GdxExchange.Market.ETHER : Coin(GdxExchange.Market.ETHER),
            GdxExchange.Market.LTC: Coin(GdxExchange.Market.LTC),
            GdxExchange.Market.BCH: Coin(GdxExchange.Market.BCH)
        }