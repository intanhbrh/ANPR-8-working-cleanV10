class AakashError(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

class VideoStreamError(Exception):
    def __init__(self, message="Video stream is not avaliable"):
        self.message = message
        super().__init__(self.message)
