import sys
sys.path.append("C:\\Users\\Rick\\PycharmProjects\\Acx-API")
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.parse
import urllib.error

from builder_clients.api_builders import *
from repository.acx_repo import*
from exchange.exchange import *
from client_server.errors import ServerError
import datetime
import json



def loadJSON(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            response = response.read().decode('utf-8')
            data = json.loads(response)
        return data
    except urllib.error.URLError as error:
        print(error)
        return None


class myHandler(BaseHTTPRequestHandler):

    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        print("Request: +"+ self.path)

        parseResult = urllib.parse.urlparse(self.path)
        path= parseResult.path.split("/")
        db = path[1]
        service= path[2]
        param_dict = urllib.parse.parse_qs(parseResult.query)

        print("params_dict: "+ str(param_dict))

        parser = ServerParser()
        response, error = parser.parseRequest(db, service, param_dict)


        if error is not None:
            self.wfile.write(bytes(error.getErrorMsg(), "utf8"))
            return

        self.wfile.write(bytes(json.dumps(response),"utf8"))

        return





class ServerInfo:
    PORT_NUMBER=8080
    SERVER_PORT=80


class PARAMS:
    HOUR ="hour"
    MINUTE = "minute"
    DAY = "day"
    MARKET = "market"
    START_DATETIME = "start_date"

    def findDatesInParams(self,param_dict):
        date = None

        if PARAMS.START_DATETIME in param_dict:
            date = param_dict[PARAMS.START_DATETIME][0]
        return date

    def stripDatesToDateTime(self,date):
        format =  '%Y-%m-%dT%H:%M'

        d = datetime.datetime.strptime(date,format)

        return d

    def findTimesInParams(self, param_dict):
        hour =None
        day =None
        minute = None

        if PARAMS.HOUR in param_dict:
            hour = int(param_dict[PARAMS.HOUR][0])
        if PARAMS.DAY in param_dict:
            day = int(param_dict[PARAMS.DAY][0])
        if PARAMS.MINUTE in param_dict:
            minute = int(param_dict[PARAMS.MINUTE][0])

        return day, hour, minute

    def findMarketInParams(self,params_dict):
        if PARAMS.MARKET not in params_dict:
            return None

        return params_dict[PARAMS.MARKET][0]


    def constructStartDate(self,year, month, day,hour= 0,minute=0):
        # Format to follow is this %Y-%m-%dT%H:%M

        def addZeroIfLenOne(digit):
            dig = str(digit)
            if(len (str(digit))==1):
                dig = "0"+dig
            return dig

        if(len(str(year))!=4):
            raise Exception("Year has to be 4 digits, given : " + str(year))

        y = str(year)
        mon = addZeroIfLenOne(month)
        d = addZeroIfLenOne(day)
        h = addZeroIfLenOne(hour)
        m = addZeroIfLenOne(minute)
        string = y+"-"+mon+"-"+d+"T"+h+":"+m
        return string




class ServerService:
    FindAll = "findall"
    FindAfter="findafter"
    FindInBetween = "findinbetween"


class ServerParser:
    def __init__(self):
        self.requestMapper = {
            ServerService.FindAll:self.parseFindAll,
            ServerService.FindAfter:self.parseFindAfterTime,
            ServerService.FindInBetween:self.parseFindInBetween
        }

        self.db ={
            GdxExchange.Name : GdxDB(),
            AcxExchange.Name : AcxDB()

        }
        self.p = PARAMS()

    def parseRequest(self,db, service,params_dict):
        if service not in self.requestMapper.keys():
            return None, ServerError("Service: "+service+" not in service provided "
                                     +str(self.requestMapper.keys()))
        response, error = self.requestMapper[service](db, params_dict)

        if error is not None:
            return None, error

        return response, None

    def fetchSystemTime(self):
        api = AcxApiBuilder()

        systemTimeUrl = api.service(AcxApiBuilder.Service.SystemTime).getAPI()

        sysTime = loadJSON(systemTimeUrl)
        if(sysTime is not None):
            readable = datetime.datetime.fromtimestamp(sysTime)
        if(sysTime is None):
            readable = datetime.datetime.now()

        return readable

    def aestToUTC(self, time):
        time = time- datetime.timedelta(hours=11)
        return time.isoformat()

    def parseFindAll(self, db, params_dict):

        market = self.p.findMarketInParams(params_dict)
        if market is None:
            error = ServerError(ServerError.Four + ": No Market Specified")
            return None, error

        repo,error = self.db[db].getRepository(market)

        if error is not None:
            return None, error

        response = list(repo.findAll())
        return response, error

    def parseFindInBetween(self,db,params_dict):

        market = self.p.findMarketInParams(params_dict)
        if market is None:
            error = ServerError(ServerError.Four + ": No Market Specified")
            return None, error

        repo, error = self.db[db].getRepository(market)
        if error is not None:
            return None, error


        date = self.p.findDatesInParams(params_dict)
        if date is None:
            error = ServerError(ServerError.Four + ": No Start Date requesting for FindInBetween")
            return None, error

        print(params_dict)
        start_date = self.p.stripDatesToDateTime(date)

        day,hour,minute = self.p.findTimesInParams(params_dict)
        if hour is None:
            hour= 0
        if day is None:
            day = 0
        if minute is None:
            minute = 0

        date_length = datetime.timedelta(days=day, hours=hour, minutes=minute)
        before_date = start_date-date_length

        start_date = start_date.isoformat()
        before_date = before_date.isoformat()
        print(start_date)
        print(before_date)

        cursor = repo.findInBetweenTime(start_date,before_date)
        return list(cursor), None


    def parseFindAfterTime(self,db,params_dict):

        market = self.p.findMarketInParams(params_dict)
        if market is None:
            error = ServerError(ServerError.Four + ": No Market Specified")
            return None, error

        repo,error = self.db[db].getRepository(market)

        if error is not None:
            return None, error



        day,hour, minute =self.p.findTimesInParams(params_dict)
        if hour is None:
            hour = 0
        if day is None:
            day = 0
        if minute is None:
            minute = 0

        offset = datetime.timedelta(days=day, hours=hour, minutes=minute)
        currtime = self.fetchSystemTime()
        currtime = (currtime - offset).isoformat()
        print(currtime)

        cursor = repo.findAfterTime(currtime)
        return list(cursor), None


class ServerRequest:
    DNS = 'http://ec2-35-169-63-106.compute-1.amazonaws.com'
    #"http://localhost:"+str(ServerInfo.PORT_NUMBER)


    def __init__(self):

        self.portnumber = ServerInfo.PORT_NUMBER
        self.rq = ServerRequest.DNS
        self.p = PARAMS()

    def database(self,db):
        if isinstance(db, GdxExchange):
            self.rq+="/"+GdxExchange.Name
        elif isinstance(db,AcxExchange):
            self.rq+="/"+AcxExchange.Name
        else:
            raise Exception("Instance: "+ db+ " is not of any Exchange")

        return self

    def getRequest(self):
        request = self.rq
        self.clear()
        return request

    def clear(self):
        self.rq = ServerRequest.DNS#+str(self.portnumber)

    def Service(self,service):
        self.rq +=("/"+service)
        return self

    def Query(self):
        self.rq +=  "?"
        return self

    def AND(self):
        self.rq+="&"
        return self

    def Date(self,date):
        self.rq+=(PARAMS.START_DATETIME+"="+str(date))
    def Day(self,day):
        self.rq+=(PARAMS.DAY+"="+str(day))
        return self

    def Hour(self,hour):
        self.rq+=(PARAMS.HOUR+"="+str(hour))
        return self

    def Minute(self,minute):
        self.rq+=(PARAMS.MINUTE+"="+str(minute))
        return self

    def Market(self,market):
        self.rq += (PARAMS.MARKET + "=" + str(market))
        return self

    def buildFindAllRequest(self, market):

        self.Service(ServerService.FindAll)
        self.Query()
        if (market is None):
            raise Exception("Market cannot be None")
        else:
            self.Market(market)

        return self.getRequest()

    def buildFindInBetweenRequest(self, db, ticker, s_year, s_month, s_day, to_day, to_hour=0):
        self.database(db)
        self.Service((ServerService.FindInBetween))
        self.Query()

        if (ticker is None):
            raise Exception("Market cannot be None")
        else:
            self.Market(ticker)

        date = self.p.constructStartDate(s_year,s_month,s_day)
        self.AND()
        self.Date(date)

        if(to_day is not None):
            self.AND()
            self.Day(to_day)
        if(to_hour is not None):
            self.AND()
            self.Hour(to_hour)

        return self.getRequest()



    '''
    Retrieves all the instances after a certain time
    '''
    def buildAfterTimeRequest(self, db, ticker, day = None, hour= None, minute= None):

        self.database(db)
        self.Service(ServerService.FindAfter)
        self.Query()

        if (ticker is None):
            raise Exception("Market cannot be None")
        else:
            self.Market(ticker)

        if(day is not None):
            self.AND()
            self.Day(day)
        if(hour is not None):
            self.AND()
            self.Hour(hour)
        if(minute is not None):
            self.AND()
            self.Minute(minute)

        return self.getRequest()

def run():


    try:
        #Create a web server and define the handler to manage the
        #incoming request
        allhosts = '0.0.0.0'
        localhost = 'localhost'
        server = HTTPServer((localhost, ServerInfo.PORT_NUMBER), myHandler)
        print ('Started httpserver on port ' , ServerInfo.PORT_NUMBER)

        #Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        server.socket.close()



if __name__ == '__main__':

    '''
    parser = ServerParser()
    response, error = parser.parseRequest(ServerService.FindAll,{PARAMS.MARKET:[AcxExchange.Market.BITCOIN]})

    if error is not None:
        print(error.getErrorMsg())
    else:
        print(response)
    '''


    request = ServerRequest()
    r = request.buildFindInBetweenRequest(GdxExchange(),"btcaud",2017,12,29,7)
    print(r)

    #p = PARAMS()
    #string= p.constructStartDate(1997,1,6,3,11)
    #print(string)
    #print(p.stripDatesToDateTime(string))
    run()

