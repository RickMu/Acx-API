
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.parse
import urllib.error

from builders.acx_builder import AcxApiBuilder,Service
from repository.acx_repo import AcxDB, MongoRepo
from client_server.errors import ServerError
import datetime
import json



def loadJSON(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:

           data = json.load(response)
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

        parseResult = urllib.parse.urlparse(self.path)
        service = parseResult.path.split("/")[1]
        param_dict = urllib.parse.parse_qs(parseResult.query)

        parser = ServerParser()
        response, error = parser.parseRequest(service, param_dict)


        if error is not None:
            self.wfile.write(bytes(error.getErrorMsg(), "utf8"))
            return

        self.wfile.write(bytes(json.dumps(response),"utf8"))

        return





class ServerInfo:
    PORT_NUMBER=8080


class PARAMS:
    HOUR ="hour"
    MINUTE = "minute"
    DAY = "day"
    MARKET = "market"

class ServerService:
    FindAll = "findall"
    FindAfter="findafter"


class ServerParser:
    def __init__(self):
        self.db = AcxDB.getAcxDB()
        self.requestMapper = {
            ServerService.FindAll:self.parseFindAll,
            ServerService.FindAfter:self.parseFindAfterTime
        }

    def parseRequest(self,service,params_dict):
        if service not in self.requestMapper.keys():
            return None, ServerError("Service: "+service+" not in service provided "
                                     +str(self.requestMapper.keys()))
        response, error = self.requestMapper[service](params_dict)

        if error is not None:
            return None, error

        return response, None

    def fetchSystemTime(self):
        api = AcxApiBuilder()

        systemTimeUrl = api.service(Service.SystemTime).getAPI()

        sysTime = loadJSON(systemTimeUrl)

        readable = datetime.datetime.fromtimestamp(sysTime)
        return readable

    def aestToUTC(self, time):
        time = time- datetime.timedelta(hours=11)
        return time.isoformat()

    def parseFindAll(self, params_dict):

        if PARAMS.MARKET not in params_dict:
            error = ServerError(ServerError.Four +": No Market Specified")
            return None, error

        market = params_dict[PARAMS.MARKET][0]
        repo,error = self.db.getRepository(market)

        if error is not None:
            return None, error

        response = list(repo.findAll())
        return response, error

    def parseFindAfterTime(self,param_dict):

        if PARAMS.MARKET not in param_dict:
            error = ServerError(ServerError.Four + ": No Market Specified")
            return None, error

        market = param_dict[PARAMS.MARKET][0]
        repo,error = self.db.getRepository(market)

        if error is not None:
            return None, error

        hour =0
        day = 0
        minute= 0
        if PARAMS.HOUR in param_dict:
            hour = int(param_dict[PARAMS.HOUR][0])
        if PARAMS.DAY in param_dict:
            day = int(param_dict[PARAMS.DAY][0])
        if PARAMS.MINUTE in param_dict:
            minute = int(param_dict[PARAMS.MINUTE][0])

        offset = datetime.timedelta(days=day, hours=hour, minutes=minute)
        currtime = self.fetchSystemTime()
        currtime = currtime - offset
        utcTime = self.aestToUTC(currtime)+"Z"
        print(utcTime)
        cursor = repo.findAfterTime(utcTime)
        return list(cursor), None



class ServerRequest:

    def __init__(self, portnumber):
        self.rq = "http://localhost:"+str(portnumber)
        self.portnumber = portnumber

    def getRequest(self):
        request = self.rq
        self.clear()
        return request

    def clear(self):
        self.rq = "localhost:"+str(self.portnumber)

    def Service(self,service):
        self.rq +=("/"+service)
        return self

    def Query(self):
        self.rq +=  "?"
        return self

    def AND(self):
        self.rq+="&"
        return self

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


    '''
    Retrieves all the instances after a certain time
    '''
    def buildAfterTimeRequest(self, market,day = None, hour= None, minute= None):

        self.Service(ServerService.FindAfter)
        self.Query()

        if (market is None):
            raise Exception("Market cannot be None")
        else:
            self.Market(market)

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
        server = HTTPServer(('localhost', ServerInfo.PORT_NUMBER), myHandler)
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

    run()

