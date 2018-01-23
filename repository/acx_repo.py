
from pymongo import MongoClient, errors
from abc import abstractmethod
from exchange.acx_exchange import AcxExchange
from Error import DataBaseError


class AcxDB():

    db = None

    def __init__(self):
        self.conn = MongoClient('localhost', 27017)
        self.BitcoinRepo = None
        self.EtherRepo = None
        self.HSRRepo = None
        self.BCHRepo = None
        self.getRepo= {
            AcxExchange.Market.BITCOIN: self.getBitcoinRepo,
            AcxExchange.Market.BCH:self.getBCHRepo,
            AcxExchange.Market.ETHER:self.getEtherRepo,
            AcxExchange.Market.HSR:self.getHSRRepo
        }

    @staticmethod
    def getAcxDB():
        if AcxDB.db is None:
            AcxDB.db = AcxDB()
        return AcxDB.db


    def getRepository(self,market):

        if market not in self.getRepo:
            error = DataBaseError("Market: "+market +" not in repository"
                                  + " "+str(self.getRepo.keys()))
            return None, error

        return self.getRepo[market](), None

    def getBitcoinRepo(self):
        if(self.BitcoinRepo is None):
            self.BitcoinRepo = MongoRepo(AcxExchange.Market.BITCOIN,self.conn)
        return self.BitcoinRepo
    def getEtherRepo(self):
        if(self.EtherRepo is None):
            self.EtherRepo = MongoRepo(AcxExchange.Market.ETHER,self.conn)
        return self.EtherRepo
    def getHSRRepo(self):
        if(self.HSRRepo is None):
            self.HSRRepo = MongoRepo(AcxExchange.Market.HSR,self.conn)
        return self.HSRRepo
    def getBCHRepo(self):
        if(self.BCHRepo is None):
            self.BCHRepo = MongoRepo(AcxExchange.Market.BCH,self.conn)
        return self.BCHRepo



class Repository():
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

    def __init__(self, type, conn):
        self.db = conn.Acx
        if(type == AcxExchange.Market.BITCOIN):
            self.cryptocoin = self.db.bitcoin
        elif(type== AcxExchange.Market.ETHER):
            self.cryptocoin = self.db.ether
        elif(type==AcxExchange.Market.HSR):
            self.cryptocoin = self.db.hsr
        elif(type== AcxExchange.Market.BCH):
            self.cryptocoin = self.db.bch

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

        return self.cryptocoin.find({'created_at': {'$gt': bottom_limit, "$lt":top_limit}}, projection={"_id": 0})

    def update(self,id, cols):
        self.cryptocoin.update({'id': id}, {"$set": cols})


'''
Tests of the above operations should be done over here
'''
if __name__ == "__main__":
    db = AcxDB()
    #cursor = db.getRepository(AcxExchange.Market.BITCOIN)[0].findAfterTime("2017-12-31T09:38:27Z")
    #cursor = db.getRepository(AcxExchange.Market.BITCOIN)[0].findLastTrade()
    cursor=db.getRepository(AcxExchange.Market.BITCOIN)[0].findInBetweenTime("2017-12-28T00:00:00",'2017-12-26T22:00:00')
    for i in cursor:
        print(i)


