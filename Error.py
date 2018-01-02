
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



