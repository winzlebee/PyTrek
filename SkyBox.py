
from pyglet.gl import *

# Use shaders to form a skybox (in this case, a spacebox)
class SkyBox(object):
    r = 100.0
    # Coordinates for a cube, listed below
    
    coords = [
        -r, -r, -r, -r, r, -r, r, r, -r, r, -r, -r, # Front face
        -r, -r, r, -r, r, r, -r, r, -r, -r, -r, -r, # Left Face
        r, -r, r, r, r, r, -r, r, r, -r, -r, r, # Back face
        r, -r, -r, r, r, -r, r, r, r, r, -r, r, # Right face
        -r, r, -r, -r, r, r, r, r, r, r, r, -r, # Top face
        -r, -r, -r, -r, -r, r, r, -r, r, r, -r, -r # Bottom face
    ]
    
    # Both are stored as quads, displayed as tris
    texcoords = [
        0.25, 0.5, 0.0, 0.5, 0.0, 0.25, 0.25, 0.25, # Front face
        0.5, 0.5, 0.5, 0.75, 0.25, 0.75, 0.25, 0.5, # Left face
        0.5, 0.25, 0.75, 0.25, 0.75, 0.5, 0.5, 0.5, # Back face
        0.25, 0.25, 0.25, 0.0, 0.5, 0.0, 0.5, 0.25, # Right face
        1.0, 0.5, 0.75, 0.5, 0.75, 0.25, 1.0, 0.25, # Top face
        0.25, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.25 # Bottom face
    ]
    
    indices = [
        0, 1, 2, 0, 3, 2,
        4, 5, 6, 4, 7, 6,
        8, 9, 10, 8, 11, 10,
        12, 13, 14, 12, 15, 14,
        16, 17, 18, 16, 19, 18,
        20, 21, 22, 20, 23, 22
    ]

    def __init__(self, image):
        self.texture = image.get_texture()
    
    def draw(self, rotx, roty):
        #glDisable(GL_DEPTH_TEST)
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glEnable(self.texture.target)
        glLoadIdentity()
        glBindTexture(self.texture.target, self.texture.id)
        glTexParameteri(self.texture.target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(self.texture.target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glRotatef(rotx, 1.0, 0.0, 0.0)
        glRotatef(roty, 0.0, 1.0, 0.0)
        
        pyglet.graphics.draw_indexed(len(self.coords)//3, GL_TRIANGLES, self.indices, ('v3f', self.coords), ('t2f', self.texcoords))
        glDisable(self.texture.target)
        #glEnable(GL_DEPTH_TEST)
        

