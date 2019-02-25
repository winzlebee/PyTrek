import random
import Map

class AbstractMap(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    # Default load function places a single object at the origin
    def load(self):
        return [Map.MapObject("origin", self.width//2, self.height//2)]

class GaussianGenerator(AbstractMap):
    def __init__(self, width, height, stdev, population):
        AbstractMap.__init__(self, width, height)
        self.stdev = stdev
        self.population = population
        
    def load(self):
        mapElements = []
        for elem in range(self.population):
            mapElements.append(Map.MapObject("MapObject" + str(elem),
                                             round(random.gauss(self.width//2, self.stdev)),
                                             round(random.gauss(self.height//2, self.stdev))))
            
        return mapElements
