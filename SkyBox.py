
from pyglet.gl import *

# Use shaders to form a skybox (in this case, a spacebox)
class SkyBox(object):
    r = 50.0
    # Coordinates for a cube, listed below
    # close bottom left (0), close top left (1), close top right (2), close bottom right (3)
    # far bottom left (4), far top left(5), far top right (6), far bottom right (7)
    coords = [
        -r, -r, -r, -r, r, -r, r, r, -r, r, -r, -r,
        -r, -r, r, -r, r, r, r, r, r, r, -r, r
    ]
    
    indices = [
        0, 1, 2, 0, 3, 2, # Front face
        0, 4, 5, 0, 1, 5, # Left face
        4, 5, 6, 4, 7, 6, # Back face
        3, 7, 6, 3, 2, 6, # Right face
        1, 5, 6, 1, 2, 6, # Top Face
        0, 4, 7, 0, 3, 7  # Bottom Face
    ]

    def __init__(self, texture):
        self.texture = texture
        
        self.texcoords = []
        self.texcoords.append(self.texture.get_region(x=3072, y=1024, width=1024, height=1024).get_texture())
        self.texcoords.append(self.texture.get_region(x=1024, y=1024, width=1024, height=1024).get_texture())
        self.texcoords.append(self.texture.get_region(x=1024, y=0, width=1024, height=1024).get_texture())
        self.texcoords.append(self.texture.get_region(x=1024, y=2048, width=1024, height=1024).get_texture())
        self.texcoords.append(self.texture.get_region(x=2048, y=1024, width=1024, height=1024).get_texture())
        self.texcoords.append(self.texture.get_region(x=0, y=1024, width=1024, height=1024).get_texture())
    
    def draw(self, rotx, roty):
        #glDisable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLoadIdentity()
        
        glRotatef(rotx, 1.0, 0.0, 0.0)
        glRotatef(roty, 0.0, 1.0, 0.0)
        
        pyglet.graphics.draw_indexed(8, GL_TRIANGLES, self.indices, ('v3f', self.coords))
        
        #glEnable(GL_DEPTH_TEST)
        

