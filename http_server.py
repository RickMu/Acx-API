
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

from AcxAPI import AcxApiBuilder, Service,loadJSON
from Repository import AcxDB, MongoRepo

import datetime



class myHandler(BaseHTTPRequestHandler):

    PORT_NUMBER=8080

    def __init__(self):
        super().__init__()
        self.db = AcxDB()
        self.repos = {
            MongoRepo.BCH : self.db.getBCHRepo(),
            MongoRepo.BITCOIN :self.db.getBitcoinRepo(),
            MongoRepo.ETHER: self.db.getEtherRepo(),
            MongoRepo.HSR: self.db.getHSRRepo(),
        }


    def fetchSystemTime(self):
        api = AcxApiBuilder()

        systemTimeUrl = api.service(Service.SystemTime).getAPI()

        sysTime = loadJSON(systemTimeUrl)

        readable = datetime.datetime.fromtimestamp(sysTime)
        return readable



    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        #message = "Hello World!"

        #self.wfile.write(bytes(message, "utf8"))
        #self.wfile.write(bytes(str(self.path.split("/")), "utf8"))

        parseResult = urllib.parse.urlparse(self.path)

        param_dict = urllib.parse.parse_qs(parseResult.query)

        day = 0
        hour = 0
        minute = 0
        market = None
        if PARAMS.MARKET in param_dict:
            market = param_dict[PARAMS.MARKET]
        else:
            self.wfile.write(bytes("Error: 200", "utf8"))

        if PARAMS.HOUR in param_dict:
            hour = int(param_dict[PARAMS.HOUR][0])
        if PARAMS.DAY in param_dict:
            day = int(param_dict[PARAMS.DAY][0])
        if PARAMS.MINUTE in param_dict:
            minute = int(param_dict[PARAMS.MINUTE][0])

        offset = datetime.timedelta(days=day,hours=hour,minutes=minute)
        currtime = self.fetchSystemTime()

        currtime = currtime - offset
        utcTime = self.aestToUTC(currtime)



        self.wfile.write(bytes(str(currtime.isoformat()),"utf8"))
        #self.wfile.write(bytes(str(parseResult), "utf8"))
        return

    def aestToUTC(self, time):
        time = time- datetime.timedelta(hours=11)
        return time.isoformat()


class PARAMS:
    HOUR ="hour"
    MINUTE = "minute"
    DAY = "day"
    MARKET = "market"

class serverRequest:

    ADDRESS = "localhost:"+str(myHandler.PORT_NUMBER)

    def __init__(self):
        self.rq= serverRequest.ADDRESS
    def AND(self):
        self.rq+="&"
    def Day(self,day):
        self.rq+=(PARAMS.DAY+"="+str(day))
    def Hour(self,hour):
        self.rq+=(PARAMS.HOUR+"="+str(hour))
    def Minute(self,minute):
        self.rq+=(PARAMS.MINUTE+"="+str(minute))

    def Market(self,market):
        self.rq += (PARAMS.MARKET + "=" + str(market))

    def request(self, market,day, hour, minute):
        self.rq= serverRequest.ADDRESS+"/?"
        if(market is None):
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
        return self.rq



def run():

    try:
        #Create a web server and define the handler to manage the
        #incoming request
        server = HTTPServer(('localhost', myHandler.PORT_NUMBER), myHandler)
        print ('Started httpserver on port ' , myHandler.PORT_NUMBER)

        #Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        server.socket.close()



if __name__ == '__main__':
    run()


