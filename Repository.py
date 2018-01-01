
from pymongo import MongoClient, errors
from abc import abstractmethod



class AcxDB():
    def __init__(self):
        self.conn = MongoClient('localhost', 27017)
        self.BitcoinRepo = None
        self.EtherRepo = None
        self.HSRRepo = None
        self.BCHRepo = None

    def getBitcoinRepo(self):
        if(self.BitcoinRepo is None):
            self.BitcoinRepo = MongoRepo(MongoRepo.BITCOIN,self.conn)
        return self.BitcoinRepo
    def getEtherRepo(self):
        if(self.EtherRepo is None):
            self.EtherRepo = MongoRepo(MongoRepo.ETHER,self.conn)
        return self.EtherRepo
    def getHSRRepo(self):
        if(self.HSRRepo is None):
            self.HSRRepo = MongoRepo(MongoRepo.HSR,self.conn)
        return self.HSRRepo
    def getBCHRepo(self):
        if(self.BCHRepo is None):
            self.BCHRepo = MongoRepo(MongoRepo.BCH,self.conn)
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
    BITCOIN = "btcaud"
    ETHER = "ethaud"
    HSR = "hsraud"
    BCH = "bchaud"
    def __init__(self, type, conn):
        self.db = conn.Acx
        if(type == MongoRepo.BITCOIN):
            self.cryptocoin = self.db.bitcoin
        elif(type== MongoRepo.ETHER):
            self.cryptocoin = self.db.ether
        elif(type== MongoRepo.HSR):
            self.cryptocoin = self.db.hsr
        elif(type== MongoRepo.BCH):
            self.cryptocoin = self.db.bch

    def insert(self, instance):
        super().insert(instance)
        try:
            self.cryptocoin.insert(instance)
        except errors.DuplicateKeyError as error:
            print(error)
    def findAll(self):
        return self.cryptocoin.find()

    def findLastTrade(self):
        return self.findMax(self.cryptocoin, "id")

    def clear(self):
        super().clear()
        self.cryptocoin.remove()

    def findMax(self, column):
        return self.sort(self.cryptocoin, column, limit=1)

    def findMin(self, column):
        return self.sort(self.cryptocoin, column, ascending=False, limit=1)

    def sort(self, column, largestFirst=True, limit=None):
        order = -1
        if (largestFirst == False):
            order = 1
        if (limit is not None):
            return self.cryptocoin.find().sort([(column, order)]).limit(limit)
        return self.cryptocoin.find().sort([(column, 1)])

    def findAfterTime(self, time):
        return self.cryptocoin.find({'created_at': {'$gt': time}})

'''
Tests of the above operations should be done over here
'''
if __name__ == "__main__":
    db = AcxDB()
    cursor = db.getBitcoinRepo().findAfterTime("2017-12-31T09:38:27Z")


