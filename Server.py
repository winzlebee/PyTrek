import pyglet
import pickle

import GalaxyView
import ThreadedServer
import messages
import Util
import UserInterface

# Map Stuff
import MapGenerator
import Map

# Generate or load a map
map_size = 32
mapLoader = MapGenerator.GaussianGenerator(map_size, map_size, 16, 24) # (width, height, spread, number)
playMap = Map.Map(map_size, map_size, mapLoader)
server_currentView = 0

def setCurrentView(view):
    global server_currentView
    server_currentView = view
    

# TODO: Change fighter image to ship-class derived image
shipImg = pyglet.resource.image("resources/ship_fighter.png")
shipImg.anchor_x = shipImg.width/2
shipImg.anchor_y = shipImg.height/2
    
server_navComponent = UserInterface.UINavElement("Navigation Map", 0, 0, 100, 100, False, shipImg, 1)
server_navComponent.setMap(playMap)

def recieveTerminalRequest(client, msg):
    message = pickle.loads(msg)
    
    if isinstance(message, messages.SpeedChangedMessage):
        # Changing the speed
        speed = Util.getSpeedFromWarpImpulse(message.warp, message.impulse)
        mainView.setSpeed(speed)
        server_navComponent.setSpeed(speed)
    elif isinstance(message, messages.HeadingChangedMessage):
        mainView.setHeading(message.heading)
    elif isinstance(message, messages.ViewChangeMessage):
        setCurrentView(message.view)
        
def clientConnected(client, address):
    # Send the client a copy of the map
    print("Client Connected:", client)
    client.send(pickle.dumps(messages.MapMessage(playMap)))
    
# Initialize the server - we're currently in the server module. Third argument is callback for recieving a request.
pt_server = ThreadedServer.PyTrekServer('', 23545, recieveTerminalRequest);
pt_server.setClientConnectCallback(clientConnected)

pt_server.start()

# Setup the window    
window = pyglet.window.Window(1280, 720, resizable=True)

# Create a User Interface to store our map object
# TODO: Updating map based on status of world
server_ui = UserInterface.PyTrekUserInterface(window)
server_ui.addNavElement(server_navComponent)

# Format is window, fov
mainView = GalaxyView.GalaxyView(window, 80)
mainView.loadMap(playMap)

@window.event
def on_draw():
    pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT | pyglet.gl.GL_DEPTH_BUFFER_BIT)
    pyglet.gl.glPushAttrib(pyglet.gl.GL_ENABLE_BIT)
    mainView.render()
    pyglet.gl.glPopAttrib(pyglet.gl.GL_ENABLE_BIT)
    if (server_currentView != 0):
        server_ui.render()

pyglet.app.run()

pt_server.close()

