
# Local Imports
import ThreadedClient
import UserInterface
import messages

import pickle
import pyglet
from pyglet.gl import *

glEnable(GL_TEXTURE_2D)
glEnable(GL_DEPTH_TEST)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

hostname = input("Enter Server IP: ")    

window = pyglet.window.Window(1280, 720, resizable=True)
helm_ui = UserInterface.PyTrekUserInterface(window)

def onclick_mapBtn(x, y):
    print("Map button has been clicked.")

# UI Components for the helm

# Navigation Element
shipImg = pyglet.resource.image("resources/ship_fighter.png")
shipImg.anchor_x = shipImg.width/2
shipImg.anchor_y = shipImg.height/2

pt_ui_initialZoom = 5

pt_ui_navElement = UserInterface.UINavElement("navigation", 20, 15, 70, 70, True, shipImg, pt_ui_initialZoom)

# Buttons
pt_ui_mapBtn = UserInterface.UIButton("mapBtn", "Map", 100-16, 100-9)
pt_ui_visBtn = UserInterface.UIButton("mapBtn", "Visual", 100-32, 100-9)
pt_ui_engBtn = UserInterface.UIButton("mapBtn", "Engineering", 100-48, 100-9)
pt_ui_mapBtn.setClickHandler(onclick_mapBtn)

# Sliders
pt_ui_sliderGroupImage = pyglet.resource.image("resources/helm_UI/background.png")

pt_ui_sliderGroup = UserInterface.UIImageElement("sliderGroup", 0, 0, 20, 50, pt_ui_sliderGroupImage)

pt_ui_warpSlider = UserInterface.UISlider("warpSlider", 3.3, 182, 5, 0, 4, True)
pt_ui_impulseSlider = UserInterface.UISlider("impulseSlider", 12.8, 240, 4, 0, 10, True)
pt_ui_zoomSlider = UserInterface.UISlider("zoomSlider", 92, 0, 3, pt_ui_initialZoom, 50, False)

# Labels for sliders
pt_ui_warpLabel = UserInterface.UILabel("warpLabel", "0", 5.4, 7.4, 16)
pt_ui_impulseLabel = UserInterface.UILabel("impulseLabel", "0", 15, 10, 8)
pt_ui_impulseLabel.setSuffix("%")

# Handlers for various things, sending messages to the big server

def sendHeadingChange(newHeading):
  msg = pickle.dumps(messages.HeadingChangedMessage(newHeading))
  helm_client.sendMessage(msg)

def sendSpeedChange():
  msg = pickle.dumps(messages.SpeedChangedMessage(pt_ui_warpSlider.getCurrentValue(), pt_ui_impulseSlider.getCurrentValue()))
  helm_client.sendMessage(msg)

def onslidechange_warpSlider(val):
    pt_ui_warpLabel.setText(str(val))
    sendSpeedChange()
    
def onslidechange_impulseSlider(val):
    pt_ui_impulseLabel.setText(str(val*10))
    sendSpeedChange()

pt_ui_navElement.setHeadingChangedHandler(sendHeadingChange)
pt_ui_warpSlider.setValueChangeHandler(onslidechange_warpSlider)
pt_ui_impulseSlider.setValueChangeHandler(onslidechange_impulseSlider)
    
def onslidechange_zoomSlider(val):
    pt_ui_navElement.setZoomLevel(val)
    
pt_ui_zoomSlider.setValueChangeHandler(onslidechange_zoomSlider)

# Buttons
helm_ui.addComponent(pt_ui_mapBtn)
helm_ui.addComponent(pt_ui_visBtn)
helm_ui.addComponent(pt_ui_engBtn)

# Sliders
helm_ui.addComponent(pt_ui_sliderGroup)
helm_ui.addComponent(pt_ui_warpSlider)
helm_ui.addComponent(pt_ui_impulseSlider)
helm_ui.addComponent(pt_ui_zoomSlider)

helm_ui.addComponent(pt_ui_warpLabel)
helm_ui.addComponent(pt_ui_impulseLabel)

# Navigation Element
helm_ui.addNavElement(pt_ui_navElement)

# Pyglet code, send messages to server somewhere in here

# Client (helm) has recieved a message from the server    
def messageRecieved(msg):
    message = pickle.loads(msg)
    print(message)
    if isinstance(message, messages.MapMessage):
        pt_ui_navElement.setMap(message.map)
        helm_client.sendMessage(pickle.dumps(messages.Message())) # Send a blank message as acknowledgement
        print("Map updated and loaded.")

helm_client = ThreadedClient.PyTrekClient(hostname)
helm_client.setMessageRecievedCallback(messageRecieved)
helm_client.start()

@window.event
def on_draw():
    pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
    pyglet.gl.glClearColor(0.0, 0.1, 0.3, 1.0)
    helm_ui.render()
    
pyglet.app.run()

if hostname:        
  helm_client.close()
