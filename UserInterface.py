import Util

import pyglet
from pyglet.window import mouse
from functools import wraps
from math import isclose

import math

# Global imports for UI Components used in the entire user interface
ui_btn = pyglet.resource.image('resources/ui_btn.png')
ui_btn_hover = pyglet.resource.image('resources/ui_btn_hover.png')

# Slider
ui_slider_top = pyglet.resource.image('resources/slider_top.png')
ui_slider_bottom = pyglet.resource.image('resources/slider_bottom.png')
ui_slider_button = pyglet.resource.image('resources/slider_button.png')
ui_slider_segment = pyglet.resource.image('resources/slider_segment.png')

# Simple user interface class. All objects are defined relative to 0-100 coordinates on the width
# and height of the screen.
class PyTrekUserInterface(object):
    def __init__(self, windowRef):
        
        self.components = []
        self.window = windowRef
        
        def getNormalizedComponent(x, y):
            for component in self.components:
                xnorm = x / self.window.width * 100
                ynorm = y / self.window.height * 100
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
                component.resizeWindow(width, height)
            # return pyglet.event.EVENT_HANDLED
                
        
    def render(self):
        # Render the whole UI
        for component in self.components:
            component.render(self.window)
            
    def getComponent(self, name):
        for component in self.components:
            if component.getName == name:
                return component
                
        return None
        
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
        
        self.hoverStatus = False
        
    # Sends the click in coordinates relative to the component's origin, in UI coordinates
    def click(self, x, y):
        if hasattr(self, 'sendClick'): self.sendClick(x, y)
        
    def hover(self, hoverStatus):
        if hasattr(self, 'sendHover'): self.sendHover(hoverStatus)
        
    def drag(self, x, y, dx, dy):
        if hasattr(self, 'sendDrag'): self.sendDrag(x, y, dx, dy)
        
    def resizeWindow(self, width, height):
        if hasattr(self, 'sendResize'): self.sendResize(width, height)
        
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
        
    def render(self, window):
        # Render as a square for the base UIComponent class
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
         ('v2f', [(self.xpos)/100*window.width, (self.ypos)/100*window.height,
                  (self.width+self.xpos)/100*window.width, (self.ypos)/100*window.height,
                  (self.width+self.xpos)/100*window.width, (self.height+self.ypos)/100*window.height,
                  (self.xpos)/100*window.width, (self.height+self.ypos)/100*window.height])) 
            
class UINavElement(UIComponent):
    def __init__(self, name, x, y, w, h, canDirect, navImage):
        UIComponent.__init__(self, name, x, y, w, h)
        
        # Default zoom level is level 1, 4 lightyears per screen unit
        self.zoomLevel = 5
        self.control = canDirect
        
        # For direction angle changes
        self.rotating = False
        self.oldDirection = 0
        self.newDirection = 0
        
        self.rotationSpeed = 90
        self.rotTimePassed = 0
        
        # The navigation image to use is passed as a constructor to the UINavElement
        self.sprite = pyglet.sprite.Sprite(img=navImage)
        
        # Update per frame based on the rotation speed of the ship
        def update_ship(delta):
            if self.rotating:
                progress = abs(self.rotTimePassed/(Util.shortAngleDist(self.oldDirection, self.newDirection)/self.rotationSpeed))
                if not progress > 1:
                    self.sprite.rotation = Util.angleSmoothLerp(self.oldDirection, self.newDirection, progress)
                    self.rotTimePassed += delta
                elif self.rotTimePassed != 0:
                    self.cancelRotation()
        
        if self.control:    
            pyglet.clock.schedule_interval(update_ship, 1/60.0)
        
        # Set the resize handler for the navigation marker
        def on_resize(width, height):
            # New window size width, height
            self.sprite.update(x=((self.xpos+self.width/2)/100)*width, y=((self.ypos+self.height/2)/100)*height, scale=(4/100*width)/(self.sprite.image.width))
            
        self.setResizeHandler(on_resize)
        
        # The nav element draws a grid with the ship in the middle. On click, it slowly rotates the ship towards the desired heading
        if self.control:
            def clickHandler(x, y):
                # Get the angle to the click that occurred
                if (self.rotating):
                    self.cancelRotation()
                    
                self.newDirection = -math.degrees(math.atan2(y-(self.width/2), x-(self.height/2))) + 90
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
        
    # Zoom factor is how much we need to scale things that are on the map
    def getZoomFactor(self):
        return 100/self.zoomLevel
        
    def render(self, window):
        numLines = round(100/self.zoomLevel+2)
    
        lines = []
        
        # Center lines
        center = [(self.xpos+self.width/2)/100*window.width, (self.ypos+self.height)/100*window.height,
                  (self.xpos + self.width/2)/100*window.width, (self.ypos)/100*window.height,
                  (self.xpos+self.width)/100*window.width, (self.ypos+self.height/2)/100*window.height,
                  (self.xpos)/100*window.width, (self.ypos+self.height/2)/100*window.height]
                           
        pyglet.gl.glColor3f(1.0, 0.3, 0.5)
        
        pyglet.graphics.draw(4, pyglet.gl.GL_LINES,
            ('v2f', center))
        
        pyglet.gl.glColor3f(1.0, 1.0, 1.0)
        
        for y in range(1, round(numLines/2)):
            interval = (100/(100/self.zoomLevel))*y
            
            # Draw a line in the middle, then draw one either side
            
                           
            lines.extend([((self.xpos+self.width/2)/100*window.width)+(interval/100*(self.width/100*window.width)), (self.ypos+self.height)/100*window.height,
                          ((self.xpos+self.width/2)/100*window.width)+(interval/100*(self.width/100*window.width)), (self.ypos)/100*window.height])
                          
            lines.extend([((self.xpos+self.width/2)/100*window.width)-(interval/100*(self.width/100*window.width)), (self.ypos+self.height)/100*window.height,
                          ((self.xpos+self.width/2)/100*window.width)-(interval/100*(self.width/100*window.width)), (self.ypos)/100*window.height])
                          
            lines.extend([((self.xpos+self.width)/100*window.width), (self.ypos+self.height/2)/100*window.height+(interval/100*(self.height/100*window.height)),
                          ((self.xpos)/100*window.width),  (self.ypos+self.height/2)/100*window.height+(interval/100*(self.height/100*window.height))])
                          
            lines.extend([((self.xpos+self.width)/100*window.width), (self.ypos+self.height/2)/100*window.height-(interval/100*(self.height/100*window.height)),
                          ((self.xpos)/100*window.width),  (self.ypos+self.height/2)/100*window.height-(interval/100*(self.height/100*window.height))])
    
        # Draw a grid, making sure that the specified zoom level of squares are displayed
        pyglet.graphics.draw((round(numLines/2)-1)*8, pyglet.gl.GL_LINES,
            ('v2f', lines))
            
        self.sprite.draw()
                
class UIButton(UIComponent):
    # Buttons are always a fixed size so we don't worry about setting their size
    def __init__(self, name, text, x, y):
        UIComponent.__init__(self, name, x, y, 16, 8)
        self.text = text
        self.sprite = pyglet.sprite.Sprite(img=ui_btn)
        self.sprite_hover = pyglet.sprite.Sprite(img=ui_btn_hover)
        self.textElement = pyglet.text.Label(text=self.text, font_name='Arial', anchor_x="center", anchor_y="center")
        
        # Set the resize handler for the buttons in the User Interface
        def on_resize(width, height):
            # New window size width, height
            self.sprite.update(x=(self.xpos/100)*width, y=(self.ypos/100)*height, scale=(self.width/100*width)/self.sprite.image.width)
            self.sprite_hover.update(x=(self.xpos/100)*width, y=(self.ypos/100)*height, scale=(self.width/100*width)/self.sprite_hover.image.width)
            
            # Placing of the text element
            self.textElement.font_size = (self.height/100)*height/4
            self.textElement.x = (self.xpos+(self.width/2))/100*width
            self.textElement.y = (self.ypos+(self.height/2))/100*height
            
        def on_hover(hover):
            if hover:
                self.textElement.color = (0, 0, 0, 255)
            else:
                self.textElement.color = (255, 255, 255, 255)
            
        self.setResizeHandler(on_resize)
        self.setHoverHandler(on_hover)
        
        
    def setText(text):
        self.text = text;
        
    def render(self, window):
        # TODO: Later we're gonna use OpenGL to do this
        if (self.hoverStatus):
            self.sprite_hover.draw()
        else:
            self.sprite.draw()
            
        self.textElement.draw()
        
class UISlider(UIComponent):
    
    # Define a slider with steps elements, a minimum value and a maxium value. Snap defines whether we should snap to the steps or not
    def __init__(self, name, x, y, steps, minVal, maxVal, snap):
        UIComponent.__init__(self, name, x, y, 4, 4*steps+16)
        self.numSteps = steps;
        self.min = minVal
        self.max = maxVal
        self.currentVal = self.min;
        
        self.snapToStep = snap
        
        self.slideBatch = pyglet.graphics.Batch()
        
        # Definition for sprites we're gonna use
        self.spriteBottom = pyglet.sprite.Sprite(img=ui_slider_bottom, batch=self.slideBatch)
        self.spriteTop = pyglet.sprite.Sprite(img=ui_slider_top, batch=self.slideBatch)
        
        self.segmentSprites = []
        for i in range(self.numSteps):
            self.segmentSprites.append(pyglet.sprite.Sprite(img=ui_slider_segment, batch=self.slideBatch))
            
        self.spriteSlider = pyglet.sprite.Sprite(img=ui_slider_button, batch=self.slideBatch)
        
        def on_resize(width, height):
            scaleFac = (self.width/100*width)/ui_slider_segment.width
        
            # Scale the segments first
            counter = 0
            for segment in self.segmentSprites:
                segment.scale = scaleFac
                segment.update(x=self.xpos/100*width, y=self.ypos/100*width+(segment.height*counter)+(segment.height/2))
                counter = counter + 1
        
            # New window size width, height
            self.spriteSlider.scale = scaleFac
            self.updateSliderPosition()
            self.spriteBottom.update(x=(self.xpos/100)*width, y=(self.ypos/100)*height, scale=scaleFac)
            self.spriteTop.update(x=(self.xpos/100)*width, y=self.ypos/100*height+(self.segmentSprites[0].height*(self.numSteps+0.5)), scale=scaleFac/3)
            
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
    
    def setValueChangeHandler(self, newFunc):
        self.sendValueChanged = newFunc
        
    # Updates the position of the slider when the value changes
    def updateSliderPosition(self):
        if self.snapToStep:
            self.spriteSlider.update(x=self.segmentSprites[0].x, y=self.segmentSprites[0].y+(round(self.currentVal-self.min)/(self.max-self.min))*(self.segmentSprites[-1].y-self.segmentSprites[0].y))
        else:
            self.spriteSlider.update(x=self.segmentSprites[0].x, y=self.segmentSprites[0].y+((self.currentVal-self.min)/(self.max-self.min))*(self.segmentSprites[-1].y-self.segmentSprites[0].y))
        
    def render(self, window):
        self.slideBatch.draw()
        
    
