import ThreadedClient
import UserInterface

import pyglet
from pyglet.gl import *

glEnable(GL_TEXTURE_2D)
glEnable(GL_DEPTH_TEST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

#hostname = input("Enter Server IP: ")

#helm_client = ThreadedClient.PyTrekClient(hostname)
#helm_client.start()

window = pyglet.window.Window(1280, 720, resizable=True)
helm_ui = UserInterface.PyTrekUserInterface(window)

def onclick_mapBtn(x, y):
    print("Map button has been clicked.")
    
def onslidechange_warpSlider(val):
    print("Warp Slider:", val)
    
def onslidechange_impulseSlider(val):
    print("Impulse Slider:", val)

# UI Components for the helm

# Navigation Element
shipImg = pyglet.resource.image("resources/ship_fighter.png")
shipImg.anchor_x = shipImg.width/2
shipImg.anchor_y = shipImg.height/2

pt_ui_initialZoom = 5

pt_ui_navElement = UserInterface.UINavElement("navigation", 15, 15, 70, 70, True, shipImg, pt_ui_initialZoom)

# Buttons
pt_ui_mapBtn = UserInterface.UIButton("mapBtn", "Map", 100-16, 100-8)
pt_ui_visBtn = UserInterface.UIButton("mapBtn", "Visual", 100-32, 100-8)
pt_ui_engBtn = UserInterface.UIButton("mapBtn", "Engineering", 100-48, 100-8)
pt_ui_mapBtn.setClickHandler(onclick_mapBtn)

# Sliders

pt_ui_impulseImg = pyglet.resource.image("resources/slider_impulse.png")

pt_ui_warpSlider = UserInterface.UISlider("warpSlider", 0, 0, 5, 0, 4, True)
pt_ui_impulseSlider = UserInterface.UISlider("impulseSlider", 8, 0, 3, 0, 10, True, pt_ui_impulseImg)
pt_ui_zoomSlider = UserInterface.UISlider("zoomSlider", 92, 0, 3, pt_ui_initialZoom, 50, False)

pt_ui_warpSlider.setValueChangeHandler(onslidechange_warpSlider)
pt_ui_impulseSlider.setValueChangeHandler(onslidechange_impulseSlider)
    
def onslidechange_zoomSlider(val):
    pt_ui_navElement.setZoomLevel(val)
    
pt_ui_zoomSlider.setValueChangeHandler(onslidechange_zoomSlider)

helm_ui.addComponent(pt_ui_mapBtn)
helm_ui.addComponent(pt_ui_visBtn)
helm_ui.addComponent(pt_ui_engBtn)  
helm_ui.addComponent(pt_ui_warpSlider)
helm_ui.addComponent(pt_ui_impulseSlider)
helm_ui.addComponent(pt_ui_zoomSlider)
helm_ui.addComponent(pt_ui_navElement)

# Pyglet code, send messages to server somewhere in here

@window.event
def on_draw():
    pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
    pyglet.gl.glClearColor(0.0, 0.1, 0.3, 1.0)
    helm_ui.render()
    
pyglet.app.run()
        
#helm_client.close()
