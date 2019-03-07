import Util
import Map

import pyglet
from pyglet.window import mouse
from functools import wraps
from math import isclose

import random
import math

# Global Font
pyglet.font.add_file('resources/font.ttf')
ui_font = 'pix PixelFJVerdana12pt'

# Global imports for UI Components used in the entire user interface
ui_btn = pyglet.resource.image('resources/ui_btn.png')
ui_btn_hover = pyglet.resource.image('resources/ui_btn_hover.png')

# Slider
ui_slider_top = pyglet.resource.image('resources/slider_top.png')
ui_slider_bottom = pyglet.resource.image('resources/slider_bottom.png')
ui_slider_button = pyglet.resource.image('resources/helm_UI/slider_button.png')
ui_slider_segment = pyglet.resource.image('resources/helm_UI/slider_single.png')

# Simple user interface class. All objects are defined relative to 0-100 coordinates on the width
# and height of the screen.
class PyTrekUserInterface(object):
    def __init__(self, windowRef):
        
        self.components = []
        self.window = windowRef
        self.xDivisions = 100;
        self.yDivisions = 100;
        
        def getNormalizedComponent(x, y):
            for component in self.components:
                xnorm = x / self.window.width * 100
                ynorm = y / self.window.height * 100
                if component.selectable:
                    if (xnorm > component.xpos and xnorm < component.xpos + component.width):
                        if (ynorm > component.ypos and ynorm < component.ypos + component.height):
                            # A click event has occurred
                            return component
            return None
        
        # Register general event handlers
        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            if button == mouse.LEFT:
                comp = getNormalizedComponent(x, y)
                if comp is not None:
                    comp.click((x / self.window.width * 100)-comp.xpos, (y / self.window.height * 100)-comp.ypos)
                
                            
        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            for component in self.components:
                xnorm = x / self.window.width * 100
                ynorm = y / self.window.height * 100
                if (xnorm > component.xpos and xnorm < component.xpos + component.width):
                    if (ynorm > component.ypos and ynorm < component.ypos + component.height):
                        # Hovering over the component
                        component.hover(True)
                        continue
                
                component.hover(False)
                
        @self.window.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            # Pass the mouse drag event to a slider if it exists
            if buttons == mouse.LEFT:
                component = getNormalizedComponent(x, y)
                if component is not None:
                    component.drag(x, y, dx, dy)
              
        # Whenever the window is resized, this should propogate through all child functions  
        @self.window.event
        def on_resize(width, height):
            for component in self.components:
                component.resizeWindow(self.uiToGlobalWidth, self.uiToGlobalHeight, self.globalToUi)
            # return pyglet.event.EVENT_HANDLED
                
    # Function to convert ui coordinates to global coordinates
    def uiToGlobalWidth(self, x):
        return x/self.xDivisions*self.window.width
        
    def uiToGlobalHeight(self, y):
        return y/self.yDivisions*self.window.height
        
    # Function to convert global coordinates to local UI coordinates
    def globalToUi(self, x, y):
        return (x / self.window.width * self.xDivisions, y / self.window.height * self.yDivisions)
        
    def render(self):
        # Render the whole UI
        for component in self.components:
            # Send a function to determine the local to global coordinate system for these elements
              component.render(self.uiToGlobalWidth, self.uiToGlobalHeight)
            
    def getComponent(self, name):
        for component in self.components:
            if component.getName == name:
                return component
                
        return None
        
    def addNavElement(self, navElement):
        self.components.insert(0, navElement)
        
    def addComponent(self, component):
        self.components.append(component)
                        
class UIComponent(object):
    # w and h are also in normalized device coordinates. The UI scales with the game
    # In a pixel-perfect manner
    def __init__(self, name, x, y, w, h):
        self.name = name
        self.xpos = x
        self.ypos = y
        self.width = w
        self.height = h
        
        # Components are selectable by default
        self.selectable = True
        self.hoverStatus = False
        
    # Sends the click in coordinates relative to the component's origin, in UI coordinates
    def click(self, x, y):
        if hasattr(self, 'sendClick'): self.sendClick(x, y)
        
    def hover(self, hoverStatus):
        if hasattr(self, 'sendHover'): self.sendHover(hoverStatus)
        
    def drag(self, x, y, dx, dy):
        if hasattr(self, 'sendDrag'): self.sendDrag(x, y, dx, dy)
        
    def resizeWindow(self, width, height, globUi):
        if hasattr(self, 'sendResize'): self.sendResize(width, height, globUi)
        
    def getName(self):
        return self.name
        
    def setClickHandler(self, clickFunc):
        self.sendClick = clickFunc
        
    def setResizeHandler(self, resizeFunc):
        self.sendResize = resizeFunc
        
    def setDragHandler(self, dragFunc):
        self.sendDrag = dragFunc
        
    def setHoverHandler(self, hoverFunc):
        def newHandler(h):
            if (h != self.hoverStatus):
                self.hoverStatus = h
                
            hoverFunc(h)
            
        self.sendHover = newHandler
        
    def render(self, xt, yt):
        # Render as a square for the base UIComponent class
        square = [xt(self.xpos), yt(self.ypos),
                  xt(self.width+self.xpos), yt(self.ypos),
                  xt(self.width+self.xpos), yt(self.height+self.ypos),
                  xt(self.xpos), yt(self.height+self.ypos)]
        
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
         ('v2f', square)) 

class UIImageElement(UIComponent):
  def __init__(self, name, x, y, w, h, image):
    UIComponent.__init__(self, name, x, y, w, h)
    
    # Images can't be selected
    self.selectable = False
    self.sprite = pyglet.sprite.Sprite(img=image)
    
    def on_resize(xt, yt, globUi):
      self.sprite.update(x=xt(self.xpos), y=yt(self.ypos), scale=xt(self.width)/self.sprite.image.width)
      
    self.setResizeHandler(on_resize)
    
  def render(self, xt, yt):
    self.sprite.draw()            

class UINavElement(UIComponent):
    def __init__(self, name, x, y, w, h, canDirect, navImage, initialZoom):
        UIComponent.__init__(self, name, x, y, w, h)
        
        # Default zoom level is level 1, 4 lightyears per screen unit
        self.initialZoom = initialZoom
        self.zoomLevel = initialZoom
        self.control = canDirect
        
        # For direction angle changes
        self.rotating = False
        self.oldDirection = 0
        self.newDirection = 0
        
        self.rotationSpeed = 45
        self.rotTimePassed = 0
        
        self.worldx = 0
        self.worldy = 0
        self.speed = 0
        
        self.map = None
        
        # The navigation image to use is passed as a constructor to the UINavElement
        self.sprite = pyglet.sprite.Sprite(img=navImage)
        
        # Add some stars to the navElement for something iteresting
        self.proceduralStars = []
        
        # Update per frame based on the rotation speed of the ship
        def update_ship(delta):
            if self.rotating:
                progress = Util.getRotationInterval(self.rotTimePassed, self.rotationSpeed, self.oldDirection, self.newDirection)
                if not progress > 1:
                    self.sprite.rotation = Util.angleSmoothLerp(self.oldDirection, self.newDirection, progress)
                    self.rotTimePassed += delta
                elif self.rotTimePassed != 0:
                    self.cancelRotation()
                    
            if self.speed > 0:
                self.moveShip(self.speed*delta)
        
        if self.control:    
            pyglet.clock.schedule_interval(update_ship, 1/60.0)
        
        # Set the resize handler for the navigation marker
        def on_resize(xt, yt, toUi):
            # New window size width, height
            self.sprite.update(x=xt(self.xpos+self.width/2), y=yt(self.ypos+self.height/2), scale=xt(4)/(self.sprite.image.width))

            self.proceduralStars.clear()
            for i in range(500):
                self.proceduralStars.append((random.random()-0.5)*xt(self.width)/initialZoom)
                self.proceduralStars.append((random.random()-0.5)*yt(self.height)/initialZoom)
            
        self.setResizeHandler(on_resize)
        
        # The nav element draws a grid with the ship in the middle. On click, it slowly rotates the ship towards the desired heading
        if self.control:
            def clickHandler(x, y):
                # Get the angle to the click that occurred
                if (self.rotating):
                    self.cancelRotation()
                    
                self.newDirection = -math.degrees(math.atan2(y-(self.width/2), x-(self.height/2))) + 90
                if hasattr(self, 'handleHeadingChange'): self.handleHeadingChange(self.newDirection)
                self.rotating = True
                
            self.setClickHandler(clickHandler)
    def setZoomLevel(self, level):
        self.zoomLevel = level
        
    def cancelRotation(self):
        self.rotTimePassed = 0
        self.oldDirection = self.sprite.rotation
        self.rotating = False
        
    # Set the number of degrees per second
    def setRotationSpeed(self, rot):
        self.rotationSpeed = rot
        
    def setHeadingChangedHandler(self, handle):
        self.handleHeadingChange = handle
        
    # Set the map that is to be displayed
    def setMap(self, newMap):
        self.map = newMap
        
    # Zoom factor is how much we need to scale things that are on the map
    def getZoomFactor(self):
        return self.zoomLevel
        
    def setSpeed(self, speed):
        self.speed = speed
        
    def moveShip(self, speed):
        self.worldx += math.sin(math.radians(self.sprite.rotation))*speed
        self.worldy += math.cos(math.radians(self.sprite.rotation))*speed
        
    def setShipPosition(self, worldx, worldy):
        self.worldx = worldx
        self.worldy = worldy
        
    def render(self, xt, yt):
        numLines = round(100/self.zoomLevel+2)
    
        lines = []
        
        # Center lines
        center = [xt(self.xpos+self.width/2), yt(self.ypos+self.height),
                  xt(self.xpos + self.width/2), yt(self.ypos),
                  xt(self.xpos+self.width), yt(self.ypos+self.height/2),
                  xt(self.xpos), yt(self.ypos+self.height/2)]
                           
        pyglet.gl.glColor3f(1.0, 0.3, 0.5)
        
        pyglet.graphics.draw(4, pyglet.gl.GL_LINES,
            ('v2f', center))
        
        pyglet.gl.glColor3f(1.0, 1.0, 1.0)

        for y in range(1, round(numLines/2)):
            interval = (100/(100/self.zoomLevel))*y
            
            # Draw a line in the middle, then draw one either side
            lines.extend([xt(self.xpos+self.width/2)+(interval/100*xt(self.width)), yt(self.ypos+self.height),
						  xt(self.xpos+self.width/2)+(interval/100*xt(self.width)), yt(self.ypos)])
						  
            lines.extend([xt(self.xpos+self.width/2)-(interval/100*xt(self.width)), yt(self.ypos+self.height),
                          xt(self.xpos+self.width/2)-(interval/100*xt(self.width)), yt(self.ypos)])
						  
            lines.extend([xt(self.xpos+self.width), yt(self.ypos+self.height/2)+(interval/100*yt(self.height)),
                          xt(self.xpos), yt(self.ypos+self.height/2)+(interval/100*yt(self.height))])
                          
            lines.extend([xt(self.xpos+self.width), yt(self.ypos+self.height/2)-(interval/100*yt(self.height)),
                          xt(self.xpos), yt(self.ypos+self.height/2)-(interval/100*yt(self.height))])
        
        pyglet.gl.glLoadIdentity()    
        
        #pyglet.gl.glScissor(round(xt(self.xpos)), round(yt(self.ypos)), round(xt(self.xpos + self.width/1.4)), round(yt(self.ypos+self.height/1.25)))
        # Draw a grid, making sure that the specified zoom level of squares are displayed

        #pyglet.gl.glEnable(pyglet.gl.GL_SCISSOR_TEST)
        
        pyglet.graphics.draw((round(numLines/2)-1)*8, pyglet.gl.GL_LINES,
            ('v2f', lines))
            
        pyglet.gl.glTranslatef(xt(self.xpos+self.width/2)-self.worldx, yt(self.ypos+self.height/2)-self.worldy, 0)
        pyglet.gl.glScalef(self.getZoomFactor(), self.getZoomFactor(), 0.0)
            
        pyglet.graphics.draw(500, pyglet.gl.GL_POINTS,
            ('v2f', self.proceduralStars))
            
        #pyglet.gl.glDisable(pyglet.gl.GL_SCISSOR_TEST)
            
        pyglet.gl.glLoadIdentity()
        
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)

        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        
        # Draw all the map markers
        for mapelem in self.map.getElements():
            xnorm = max(0, min(1, (((mapelem.x-self.worldx)/self.map.width)-0.5)*(self.getZoomFactor())+0.5))
            ynorm = max(0, min(1, (((mapelem.y-self.worldy)/self.map.height)-0.5)*(self.getZoomFactor())+0.5))
            mapelem.getImage().blit(xt(self.xpos + self.width*xnorm), yt(self.ypos + self.height*ynorm))
            
        pyglet.gl.glDisable(pyglet.gl.GL_BLEND)
        
        # Draw the ship at the very last time    
        self.sprite.draw()
         
class UILabel(UIComponent):
    def __init__(self, name, text, x, y, font_size):
        UIComponent.__init__(self, name, x, y, 2, 2)
        self.selectable = False
        self.text = text
        self.suffix = ""
        self.prefix = ""
        
        self.offset_x = 0
        self.offset_y = 0
        
        self.textElement = pyglet.text.Label(font_name=ui_font, anchor_x="center", anchor_y="center", font_size=font_size)
        
        def on_resize(xt, yt, toUi):
            self.textElement.x = xt(self.xpos) + self.offset_x
            self.textElement.y = yt(self.ypos) + self.offset_y
            
        self.setResizeHandler(on_resize)
        self.update()
        
    def setPerPixelOffset(self, x, y):
        self.offset_x = x
        self.offset_y = y
        
    def update(self):
        self.textElement.text = self.prefix + self.text + self.suffix
        
    def setText(self, text):
        self.text = text
        self.update()
        
    def setPrefix(self, text):
        self.prefix = text
        self.update()
        
    def setSuffix(self, text):
        self.suffix = text
        self.update()
        
    def render(self, xt, yt):
        self.textElement.draw()
    
        
class UIButton(UIComponent):
    # Buttons are always a fixed size so we don't worry about setting their size
    def __init__(self, name, text, x, y):
        UIComponent.__init__(self, name, x, y, 16, 8)
        self.text = text
        self.sprite = pyglet.sprite.Sprite(img=ui_btn)
        self.sprite_hover = pyglet.sprite.Sprite(img=ui_btn_hover)
        self.textElement = pyglet.text.Label(text=self.text, font_name=ui_font, anchor_x="center", anchor_y="center")
        
        # Set the resize handler for the buttons in the User Interface
        def on_resize(xt, yt, toUi):
            # New window size width, height
            self.sprite.update(x=xt(self.xpos), y=yt(self.ypos), scale_x=xt(self.width)/self.sprite.image.width, scale_y=yt(self.height)/self.sprite.image.height)
            self.sprite_hover.update(x=xt(self.xpos), y=yt(self.ypos), scale_x=xt(self.width)/self.sprite_hover.image.width, scale_y=yt(self.height)/self.sprite.image.height)
            
            # Placing of the text element
            self.textElement.font_size = xt(self.width)/20
            self.textElement.x = xt(self.xpos+(self.width/2))
            self.textElement.y = yt(self.ypos+(self.height/2))
            
        def on_hover(hover):
            if hover:
                self.textElement.color = (0, 0, 0, 255)
            else:
                self.textElement.color = (255, 255, 255, 255)
            
        self.setResizeHandler(on_resize)
        self.setHoverHandler(on_hover)
        
        
    def setText(text):
        self.text = text;
        self.textElement.text = text
        
    def render(self, xt, yt):
        # TODO: Later we're gonna use OpenGL to do this
        if (self.hoverStatus):
            self.sprite_hover.draw()
        else:
            self.sprite.draw()
            
        self.textElement.draw()
        
class UISlider(UIComponent):
    
    # Define a slider with steps elements, a minimum value and a maxium value. Snap defines whether we should snap to the steps or not
    def __init__(self, name, x, y, steps, minVal, maxVal, snap):
        UIComponent.__init__(self, name, x, y, 4, 4*steps)
        self.numSteps = steps;
        self.min = minVal
        self.max = maxVal
        self.currentVal = self.min;
        self.origYPos = y
        
        self.snapToStep = snap
        
        self.slideBatch = pyglet.graphics.Batch()
        
        # Definition for sprites we're gonna use
        #self.spriteBottom = pyglet.sprite.Sprite(img=ui_slider_bottom, batch=self.slideBatch)
        #self.spriteTop = pyglet.sprite.Sprite(img=topImg, batch=self.slideBatch)
        
        self.segmentSprites = []
        for i in range(self.numSteps):
            self.segmentSprites.append(pyglet.sprite.Sprite(img=ui_slider_segment, batch=self.slideBatch))
            
        self.spriteSlider = pyglet.sprite.Sprite(img=ui_slider_button, batch=self.slideBatch)
        
        def on_resize(xt, yt, toUi):
            scaleFac = xt(self.width)/ui_slider_segment.width
                
            pixelPos = self.origYPos * scaleFac
        
            # Scale the segments first
            counter = 0
            for segment in self.segmentSprites:
                segment.scale = scaleFac
                segment.update(x=xt(self.xpos), y=pixelPos+(segment.height*counter)) # Add a half because of the bottom slider image if using it
                counter = counter + 1
                
            self.height = toUi(0, segment.height*counter)[1]
            self.ypos = toUi(0, pixelPos)[1]
                
            # New window size width, height
            self.spriteSlider.scale = xt(self.width)/ui_slider_button.width
            self.updateSliderPosition()
            #self.spriteBottom.update(x=xt(self.xpos), y=yt(self.ypos), scale=xt(self.width)/ui_slider_bottom.width)
            #self.spriteTop.update(x=xt(self.xpos), y=yt(self.ypos)+(self.segmentSprites[0].height*(self.numSteps)), scale=xt(self.width)/topImg.width)
            
        self.snapLastVal = 0
        # Called when a drag occurs on the slider
        def on_drag(x, y, dx, dy):
            # Get and set the drag value
            #if y > self.spriteSlider.y and y < self.spriteSlider.y+self.spriteSlider.height:
            change = dy/(self.segmentSprites[-1].y - self.segmentSprites[0].y)*(self.max-self.min)
            if self.currentVal + change > self.min and self.currentVal + change < self.max:
                self.currentVal += change
                
                # If we're snapping, we need to only send the value if it's changed
                if self.snapToStep:
                    if self.snapLastVal != round(self.currentVal):
                        sendVal = round(self.currentVal)
                        self.slideChanged(sendVal)
                        self.snapLastVal = sendVal
                else:
                    self.slideChanged(self.currentVal)
                
                self.updateSliderPosition()
                
        self.setDragHandler(on_drag)
        self.setResizeHandler(on_resize)
        
    def slideChanged(self, newVal):
        if hasattr(self, 'sendValueChanged'): 
            self.sendValueChanged(max(0, newVal))
            
    def getCurrentValue(self):
        if self.snapToStep:
          return round(self.currentVal)
        else:
          return self.currentVal
    
    def setValueChangeHandler(self, newFunc):
        self.sendValueChanged = newFunc
        
    # Updates the position of the slider when the value changes
    def updateSliderPosition(self):
        if self.snapToStep:
            self.spriteSlider.update(x=self.segmentSprites[0].x, y=self.segmentSprites[0].y+(round(self.currentVal-self.min)/(self.max-self.min))*(self.segmentSprites[-1].y-self.segmentSprites[0].y))
        else:
            self.spriteSlider.update(x=self.segmentSprites[0].x, y=self.segmentSprites[0].y+((self.currentVal-self.min)/(self.max-self.min))*(self.segmentSprites[-1].y-self.segmentSprites[0].y))
        
    def render(self, xt, yt):
        self.slideBatch.draw()
        
    
