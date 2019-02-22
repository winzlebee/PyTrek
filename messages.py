
class SpeedChangedMessage:
  def __init__(self, newWarp, newImpulse):
    self.warp = newWarp
    self.impulse = newImpulse
    
class HeadingChangedMessage:
  def __init__(self, newHeading):
    self.heading = newHeading
