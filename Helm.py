import ThreadedClient
import UserInterface

import pyglet
from pyglet.gl import *

glEnable(GL_TEXTURE_2D)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

#hostname = input("Enter Server IP: ")

#helm_client = ThreadedClient.PyTrekClient(hostname)
#helm_client.start()

window = pyglet.window.Window(1280, 720, resizable=True)
helm_ui = UserInterface.PyTrekUserInterface(window)

def onclick_mapBtn():
    print("Map button has been clicked.")

# UI Components for the helm
pt_ui_mapBtn = UserInterface.UIButton("mapBtn", "Map", 100-16, 100-8)
pt_ui_visBtn = UserInterface.UIButton("mapBtn", "Visual", 100-16, 100-16)
pt_ui_engBtn = UserInterface.UIButton("mapBtn", "Engineering", 100-16, 100-24)
pt_ui_mapBtn.setClickHandler(onclick_mapBtn)

helm_ui.addComponent(pt_ui_mapBtn)
helm_ui.addComponent(pt_ui_visBtn)
helm_ui.addComponent(pt_ui_engBtn)  

# Pyglet code, send messages to server somewhere in here

@window.event
def on_draw():
    pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
    helm_ui.render()
    
pyglet.app.run()
        
#helm_client.close()
