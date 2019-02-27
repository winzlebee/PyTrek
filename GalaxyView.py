from pyglet.gl import *

import random
import math
import Util

import SkyBox

# This class encapsulates all things to do with displaying a view of the galaxy
class GalaxyView:
    def __init__(self, window, fov):
        # View variables - not influenced by the network state
        self.view_numStars = 10000
        self.view_starStdDev = 128
        self.view_window = window
        self.view_fov = fov
        
        self.view_stars = self.generateStars();
        self.view_skybox = SkyBox.SkyBox(pyglet.resource.image('resources/galaxy_view/skybox1.png'))
        
        # Spaceship Variables
        self.spaceshipSpeed = 0.0
        self.spaceshipPosition = [0, 0, 0]
        self.spaceshipRotation = [0, 0, 0]
        
        # Timing for view rotation events TODO: Move spaceship attributes into separate serializable class
        self.rotating = False
        self.rotTimePassed = 0
        self.oldRotation = 0
        self.newRotation = 0
        
        def update(delta):
            # Perform rotation then movement
            if self.rotating:
                progress = Util.getRotationInterval(self.rotTimePassed, 45, self.oldRotation, self.newRotation)
                if not progress > 1:
                    self.setRotation([0.0, Util.angleSmoothLerp(self.oldRotation, self.newRotation, progress), 0.0])
                    self.rotTimePassed += delta
                elif self.rotTimePassed != 0:
                    self.cancelRotation()
                
            self.move(self.spaceshipSpeed*delta)

        pyglet.clock.schedule_interval(update, 1/60.0)
        
        @window.event
        def on_resize(width, height):
            glViewport(0, 0, width, height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(self.view_fov, width / float(height), 0.1, 1000)
            glMatrixMode(GL_MODELVIEW)
            return pyglet.event.EVENT_HANDLED
                
    def generateStars(self):
        stars = []
        for i in range(self.view_numStars*3):
            stars.append((random.gauss(0.0, self.view_starStdDev)-0.5))
        return stars
    
    # Moves the spaceship along the correct direction TODO: add rising and falling to second argument
    def move(self, movement):
        self.spaceshipPosition = [self.spaceshipPosition[0] + movement*math.cos(math.radians(self.spaceshipRotation[1]+90)),
                                  self.spaceshipPosition[1],
                                  self.spaceshipPosition[2] + movement*math.sin(math.radians(self.spaceshipRotation[1]+90))]
        #self.spaceshipPosition = [x + y for x, y in zip(self.spaceshipPosition, movement)]
        
    def rotate(self, rotation):
        # Combine the rotation and make it modulo 360 for compatability
        self.spaceshipRotation = [(x + y) % 360 for x, y in zip(self.spaceshipRotation, rotation)]
        
    def setPosition(self, x, y, z):
        self.spaceshipPosition = [x, y, z]
    
    def setRotation(self, rot):
        self.spaceshipRotation = rot
        
    def setSpeed(self, speed):
        self.spaceshipSpeed = speed
        
    # A map can be loaded. Then its corresponding objects will be displayed
    def loadMap(self, mapLoad):
        self.map = mapLoad
        
    def cancelRotation(self):
        self.rotTimePassed = 0
        self.oldRotation = self.spaceshipRotation[1]
        self.rotating = False
    
    def setHeading(self, newHeading):
        # Sets a new heading for the spaceship so it smoothly goes toward it
        if self.rotating:
            # If we're already rotating, use whatever the current rotation is as the old rotation
            self.cancelRotation()
        self.rotating = True
        self.newRotation = newHeading
        
    def render(self):
    
        # Draw the skybox

    
        pyglet.graphics.draw(self.view_numStars, GL_POINTS, ("v3f", self.view_stars))
        # Move the camera
        glLoadIdentity()
        
        # TODO: Add spaceship position offset here before matrix transformation
        glRotatef(self.spaceshipRotation[0], 1.0, 0.0, 0.0)
        glRotatef(self.spaceshipRotation[1], 0.0, 1.0, 0.0)
        glRotatef(self.spaceshipRotation[2], 0.0, 0.0, 1.0)
        glTranslatef(*self.spaceshipPosition)       
        
