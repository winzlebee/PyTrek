import datetime

class Message(object):
    def __init__(self, msgTime=datetime.datetime.now()):
        self.time = msgTime

class SpeedChangedMessage(Message):
    def __init__(self, newWarp, newImpulse):
        self.warp = newWarp
        self.impulse = newImpulse
    
class HeadingChangedMessage(Message):
    def __init__(self, newHeading):
        self.heading = newHeading
    
class MapMessage(Message):
    def __init__(self, mapObj):
        # Map object should be serializable so simply use it raw
        self.map = mapObj
    
