import pyglet
import pickle

import GalaxyView
import ThreadedServer
import messages
import Util

# Map Stuff
import MapGenerator
import Map

# Generate or load a map
map_size = 64
mapLoader = MapGenerator.GaussianGenerator(map_size, map_size, 64, 24) # (width, height, spread, number)
playMap = Map.Map(map_size, map_size, mapLoader)

def recieveTerminalRequest(client, msg):
    message = pickle.loads(msg)
    
    if isinstance(message, messages.SpeedChangedMessage):
        # Changing the speed
        mainView.setSpeed(Util.getSpeedFromWarpImpulse(message.warp, message.impulse))
    elif isinstance(message, messages.HeadingChangedMessage):
        mainView.setHeading(message.heading)
        
def clientConnected(client, address):
    # Send the client a copy of the map
    print("Client Connected:", client)
    client.send(pickle.dumps(messages.MapMessage(playMap)))
    
# Initialize the server - we're currently in the server module. Third argument is callback for recieving a request.
pt_server = ThreadedServer.PyTrekServer('', 23545, recieveTerminalRequest);
pt_server.setClientConnectCallback(clientConnected)

pt_server.start()

# Setup the window    
window = pyglet.window.Window(1280, 720)

# Format is window, fov
mainView = GalaxyView.GalaxyView(window, 80)
mainView.loadMap(playMap)

@window.event
def on_draw():
    pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
    mainView.render()

pyglet.app.run()

pt_server.close()

