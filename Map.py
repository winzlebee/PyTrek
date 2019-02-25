
import pyglet
import MapGenerator

# Atlas containing all of the map markers
map_markers = pyglet.resource.image("resources/map/markers.png")

def getMarker(name):
    marker = None
    if name == 'marker':
        marker = map_markers.get_region(0, 0, 32, 32)
    
    marker.anchor_x = marker.width/2
    marker.anchor_y = marker.height/2
    return marker

# The map class is higher-order. It only concerns itself with where things are placed on the map, not the drawing of the map
class Map(object):
    def __init__(self, width, height, abMap):
        # Initialize a map with a specified width and height
        self.width = width
        self.height = height
        
        # Maps are organised so that one unit in OpenGL terms is one unit on the map.
        # At the moment the definition of a unit is left to the imagination
        self.elements = abMap.load()
        
    def addObject(self, ob):
        self.elements.append(ob)
        
    def getElements(self):
        return self.elements
    
    
class MapObject(object):
    def __init__(self, name, xpos, ypos):
        self.name = name
        self.x = xpos
        self.y = ypos
        
        self.img = 'marker'
        
    def getImage(self):
        return getMarker(self.img)
        
    def getSprite(self):
        return pyglet.sprite.Sprite(img=self.getImage())
        
    
