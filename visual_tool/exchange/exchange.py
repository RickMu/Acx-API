from collections import defaultdict
from visual_tool.models.coin_model import Coin
class AcxExchange:
    Name = 'acx'
    class Ticker:
        BITCOIN = "btcaud"
        ETHER = "ethaud"
        HSR = "hsraud"
        BCH = "bchaud"

    def __init__(self):
        self.coins ={
            AcxExchange.Ticker.BITCOIN: Coin(AcxExchange.Ticker.BITCOIN),
            AcxExchange.Ticker.ETHER : Coin(AcxExchange.Ticker.ETHER),
            AcxExchange.Ticker.HSR: Coin(AcxExchange.Ticker.HSR),
            AcxExchange.Ticker.BCH: Coin(AcxExchange.Ticker.BCH)
        }


class GdxExchange:

    Name ='gdx'
    class Ticker:
        BITCOIN = 'BTC-USD'
        ETHER = 'ETH-USD'
        LTC =  'LTC-USD'
        BCH = 'BCH-USD'

    def __init__(self):
        self.coins ={
            GdxExchange.Ticker.BITCOIN: Coin(GdxExchange.Ticker.BITCOIN),
            GdxExchange.Ticker.ETHER : Coin(GdxExchange.Ticker.ETHER),
            GdxExchange.Ticker.LTC: Coin(GdxExchange.Ticker.LTC),
            GdxExchange.Ticker.BCH: Coin(GdxExchange.Ticker.BCH)
        }