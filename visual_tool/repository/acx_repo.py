
from pymongo import MongoClient, errors
from abc import abstractmethod
from visual_tool.exchange.exchange import *
from Error import DataBaseError
'''

class AcxDB():
    def __init__(self):
        self.conn = DBMapper.source.Acx
        self.BitcoinRepo = None
        self.EtherRepo = None
        self.HSRRepo = None
        self.BCHRepo = None
        self.getRepo= {
            AcxExchange.Ticker.BITCOIN: self.getBitcoinRepo,
            AcxExchange.Ticker.BCH:self.getBCHRepo,
            AcxExchange.Ticker.ETHER:self.getEtherRepo,
            AcxExchange.Ticker.HSR:self.getHSRRepo
        }

    def getRepository(self,market):

        if market not in self.getRepo:
            error = DataBaseError("Market: "+market +" not in repository"
                                  + " "+str(self.getRepo.keys()))
            return None, error

        return self.getRepo[market](), None

    def getBitcoinRepo(self):
        if(self.BitcoinRepo is None):
            self.BitcoinRepo = MongoRepo(self.conn.bitcoin)
        return self.BitcoinRepo
    def getEtherRepo(self):
        if(self.EtherRepo is None):
            self.EtherRepo = MongoRepo(self.conn.ether)
        return self.EtherRepo
    def getHSRRepo(self):
        if(self.HSRRepo is None):
            self.HSRRepo = MongoRepo(self.conn.hsr)
        return self.HSRRepo
    def getBCHRepo(self):
        if(self.BCHRepo is None):
            self.BCHRepo = MongoRepo(self.conn.bch)
        return self.BCHRepo


class GdxDB():
    def __init__(self):
        self.conn = DBMapper.db.Gdx
        self.BitcoinRepo = None
        self.EtherRepo = None
        self.BCHRepo = None
        self.LTCRepo = None
        self.getRepo = {
            GdxExchange.Ticker.BITCOIN: self.getBitcoinRepo,
            GdxExchange.Ticker.BCH: self.getBCHRepo,
            GdxExchange.Ticker.ETHER: self.getEtherRepo,
            GdxExchange.Ticker.LTC: self.getLTCRepo
        }

    def getRepository(self, market):

        if market not in self.getRepo:
            error = DataBaseError("Market: " + market + " not in repository"
                                  + " " + str(self.getRepo.keys()))
            return None, error

        return self.getRepo[market](), None

    def getBitcoinRepo(self):
        if (self.BitcoinRepo is None):
            self.BitcoinRepo = MongoRepo(self.conn.bitcoin)
        return self.BitcoinRepo

    def getEtherRepo(self):
        if (self.EtherRepo is None):
            self.EtherRepo = MongoRepo(self.conn.ether)
        return self.EtherRepo

    def getLTCRepo(self):
        if (self.LTCRepo is None):
            self.LTCRepo = MongoRepo(self.conn.ltc)
        return self.LTCRepo

    def getBCHRepo(self):
        if (self.BCHRepo is None):
            self.BCHRepo = MongoRepo(self.conn.bch)
        return self.BCHRepo

'''

class GdxDB:
    NAME = 'Gdx'
    BTC = "bitcoin"
    BCH = "bch"
    ETH ="ether"
    LTC = "ltc"

    def __init__(self,source):
        self.db = source.Gdx
        self.collections={
            GdxDB.BTC:self.db.bitcoin,
            GdxDB.LTC:self.db.ltc,
            GdxDB.ETH:self.db.ether,
            GdxDB.BCH:self.db.bch
        }



class AcxDB:
    NAME = 'Acx'
    BTC = "bitcoin"
    BCH = "bch"
    ETH = "ether"
    HSR = "hsr"

    def __init__(self, source):
        self.db = source.Acx
        self.collections = {
            AcxDB.BTC: self.db.bitcoin,
            AcxDB.HSR: self.db.hsr,
            AcxDB.ETH: self.db.ether,
            AcxDB.BCH: self.db.bch
        }


class DBMapper:

    DBs = {
        GdxDB.NAME:GdxDB,
        AcxDB.NAME: AcxDB
    }
    @staticmethod
    def getConn(source, db,collection):
        return DBMapper.DBs[db](source).collections[collection]



class Repository():

    @abstractmethod
    def selectRepo(self,db):
        return

    @abstractmethod
    def insert(self, instance):
        return

    @abstractmethod
    def findAll(self):
        return
    @abstractmethod
    def clear(self):
        return



class MongoRepo(Repository):

    Repo = None

    @staticmethod
    def getRepo():
        if MongoRepo.Repo is None:
            MongoRepo.Repo = MongoRepo()

        return MongoRepo.Repo

    def __init__(self):
        self.source = MongoClient('localhost', 27017)
        self.cryptocoin = None

    def setDatabaseCollection(self,db,collection):
        self.cryptocoin = DBMapper.getConn(db,collection)
        if self.cryptocoin is None:
            error = DataBaseError("Either Database: " + db + "or collection: "+ collection +" are not in repository")
            return error
        return None



    def insert(self, instance):
        super().insert(instance)
        try:
            self.cryptocoin.insert(instance)
        except errors.DuplicateKeyError as error:
            print(error)
    def findAll(self):
        return self.cryptocoin.find({},{'_id':0})

    def findLastTrade(self):
        return self.findMax("id")

    def clear(self):
        super().clear()
        self.cryptocoin.remove()

    def findMax(self, column):
        return self.sort(column, limit=1)

    def findMin(self, column):
        return self.sort( column, ascending=False, limit=1)

    def sort(self, column, largestFirst=True, limit=None):
        order = -1
        if (largestFirst == False):
            order = 1
        if (limit is not None):
            return self.cryptocoin.find(projection={"_id":False}).sort([(column, order)]).limit(limit)
        return self.cryptocoin.find(projection={"_id":False}).sort([(column, order)]).limit(100)

    def findAfterTime(self, time):
        return self.cryptocoin.find({'created_at': {'$gt': time}},{"_id":0})

    def findInBetweenTime(self,top_limit, bottom_limit):

        return self.cryptocoin.find({'created_at': {'$gte': bottom_limit, "$lt":top_limit}}, projection={"_id": 0})

    def update(self,id, cols):
        self.cryptocoin.update({'id': id}, {"$set": cols})


'''
Tests of the above operations should be done over here
'''
if __name__ == "__main__":
    source = AcxDB()
    cursor = source.getRepository(AcxExchange.Ticker.BITCOIN)[0].findAfterTime("2018-02-02T09:38:27")
    #cursor = db.getRepository(AcxExchange.Market.BITCOIN)[0].findLastTrade()
    #cursor=db.getRepository(AcxExchange.Ticker.BITCOIN)[0].findInBetweenTime("2017-12-28T00:00:00", '2017-12-26T22:00:00')
    for i in cursor:
        print(i)


