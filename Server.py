from pyglet.gl import *
from pyglet.window import key

import random
import ThreadedServer
import pickle
import messages
import Util

pt_numStars = 10000
pt_starStdDev = 5

pt_spaceshipSpeed = 0.0
pt_spaceshipPosition = [0.0, 0.0, 0.0]
pt_spaceshipRotation = [0.0, 0.0, 0.0]

pt_rotating = False
pt_rotTimePassed = 0
pt_oldRotation = 0
pt_newRotation = 0

# Generates random stars in a nebula centred on the origin
def generateStars(numStars, stdDev):
    stars = []
    for i in range(numStars*3):
        stars.append((random.gauss(0.0, stdDev)-0.5))
    return stars

def move(movement):
    global pt_spaceshipPosition
    pt_spaceshipPosition = [x + y for x, y in zip(pt_spaceshipPosition, movement)]

def rotate(rotation):
    global pt_spaceshipRotation
    # Combine the rotation and make it modulo 360 for compatability
    pt_spaceshipRotation = [(x + y) % 360 for x, y in zip(pt_spaceshipRotation, rotation)]
    
def setRotation(rot):
    global pt_spaceshipRotation
    pt_spaceshipRotation = rot
   
def recieveTerminalRequest(client, msg):
    global pt_spaceshipSpeed
    global pt_rotating, pt_newRotation
    
    message = pickle.loads(msg)
    
    if isinstance(message, messages.SpeedChangedMessage):
        # Changing the speed
        pt_spaceshipSpeed = message.warp + (message.impulse*0.1)
    elif isinstance(message, messages.HeadingChangedMessage):
        if pt_rotating:
            # If we're already rotating, use whatever the current rotation is as the old rotation
            cancelRotation()
        pt_rotating = True
        pt_newRotation = message.heading
        print("New Rotation recieved:", pt_newRotation)
        
    
# Initialize the server - we're currently in the server module
pt_server = ThreadedServer.PyTrekServer('', 23545, recieveTerminalRequest);
pt_server.start()

# Setup the window    
window = pyglet.window.Window(1280, 720)
keys = key.KeyStateHandler()

def cancelRotation():
    global pt_rotTimePassed, pt_oldRotation, pt_rotating
    pt_rotTimePassed = 0
    pt_oldRotation = pt_spaceshipRotation[1]
    pt_rotating = False

def update(delta):
    global pt_rotTimePassed
    
    # Perform rotation then movement
    if pt_rotating:
        progress = Util.getRotationInterval(pt_rotTimePassed, 45, pt_oldRotation, pt_newRotation)
        if not progress > 1:
            setRotation([0.0, Util.angleSmoothLerp(pt_oldRotation, pt_newRotation, progress), 0.0])
            pt_rotTimePassed += delta
        elif pt_rotTimePassed != 0:
            cancelRotation()
        
    move([0.0, 0.0, pt_spaceshipSpeed*delta])

# Set the logic to run at 60hz
pyglet.clock.schedule_interval(update, 1/60.0)

stars = generateStars(pt_numStars, pt_starStdDev);

@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    pyglet.graphics.draw(pt_numStars, GL_POINTS, ("v3f", stars))
    
    # Move the camera
    glLoadIdentity()
    
    # TODO: Add spaceship position offset here before matrix transformation
    
    glRotatef(pt_spaceshipRotation[0], 1.0, 0.0, 0.0)
    glRotatef(pt_spaceshipRotation[1], 0.0, 1.0, 0.0)
    glRotatef(pt_spaceshipRotation[2], 0.0, 0.0, 1.0)
    glTranslatef(*pt_spaceshipPosition)

@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(80, width / float(height), 0.1, 1000)
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED

pyglet.app.run()

pt_server.close()

