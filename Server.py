import pyglet

import GalaxyView
import ThreadedServer
import pickle
import messages
import Util

def recieveTerminalRequest(client, msg):
    message = pickle.loads(msg)
    
    if isinstance(message, messages.SpeedChangedMessage):
        # Changing the speed
        mainView.setSpeed(Util.getSpeedFromWarpImpulse(message.warp, message.impulse))
    elif isinstance(message, messages.HeadingChangedMessage):
        mainView.setHeading(message.heading)
        
    
# Initialize the server - we're currently in the server module. Third argument is callback for recieving a request.
pt_server = ThreadedServer.PyTrekServer('', 23545, recieveTerminalRequest);
pt_server.start()

# Setup the window    
window = pyglet.window.Window(1280, 720)

# Format is window, fov
mainView = GalaxyView.GalaxyView(window, 80)

@window.event
def on_draw():
    pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
    mainView.render()

pyglet.app.run()

pt_server.close()

