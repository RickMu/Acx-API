
from abc import abstractmethod
class Error:
    @abstractmethod
    def getErrorMsg(self):
        return


class DataBaseError(Error):
    def __init__(self, error_msg):
        self.msg= error_msg

    def getErrorMsg(self):
        super().getErrorMsg()
        return self.msg



class ServerError(Error):
    One = "100" #Client inappropriate actions
    Two = "200" #Success
    Three = "300"  #File Moved
    Four = "400"  #Client Error
    Five = "500"  #Server Error

    def __init__(self, erro_msg):
        self.msg = erro_msg

    def getErrorMsg(self):
        return self.msg



