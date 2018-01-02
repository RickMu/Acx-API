from Error import Error

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

