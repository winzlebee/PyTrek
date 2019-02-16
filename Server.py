from pyglet.gl import *
from pyglet.window import key

import random
import ThreadedServer

pt_numStars = 5000
pt_starStdDev = 3

pt_spaceshipSpeed = 0.0
pt_spaceshipPosition = [0.0, 0.0, 0.0]
pt_spaceshipRotation = [0.0, 0.0, 0.0]

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
   
def recieveTerminalRequest(client, msg):
    global pt_spaceshipSpeed
    finalMsg = msg.decode()
    print("Message Recieved:", finalMsg)
    
    if finalMsg[0] == 'w':
        # We're changing warp level
        pt_spaceshipSpeed = float(finalMsg[1:])
    
# Initialize the server - we're currently in the server module
pt_server = ThreadedServer.PyTrekServer('', 23545, recieveTerminalRequest);
pt_server.start()

# Setup the window    
window = pyglet.window.Window(1280, 720)
keys = key.KeyStateHandler()

def update(delta):
    if keys[key.A]:
        rotate([0.0, -40.0*delta, 0.0])
    elif keys[key.D]:
        rotate([0.0, 40.0*delta, 0.0])
        
    move([0.0, 0.0, pt_spaceshipSpeed*delta])

# Set the logic to run at 60hz
pyglet.clock.schedule_interval(update, 1/60.0)

stars = generateStars(pt_numStars, pt_starStdDev);

# Input handling. For now we just override spaceship speed.
@window.event
def on_key_press(symbol, modifiers):
    global pt_spaceshipSpeed
    if symbol == key.W:
        pt_spaceshipSpeed = pt_spaceshipSpeed + 1.0
    if symbol == key.S:
        pt_spaceshipSpeed = pt_spaceshipSpeed - 1.0

window.push_handlers(keys)

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

