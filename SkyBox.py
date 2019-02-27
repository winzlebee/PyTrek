
from pyglet.gl import *

class SkyBox(object):
    r = 50.0
    coords = [
    (( r, -r, -1), ( r,  r, -1), (-r,  r, -1), (-r, -r, -1)), # ft
    ((-r, -r,  1), (-r,  r,  1), ( r,  r,  1), ( r, -r,  1)), # bk
    ((-1, -r, -r), (-1,  r, -r), (-1,  r,  r), (-1, -r,  r)), # lt
    (( 1, -r,  r), ( 1,  r,  r), ( 1,  r, -r), ( 1, -r, -r)), # rt
    (( r,  1,  r), (-r,  1,  r), (-r,  1, -r), ( r,  1, -r)), # up
    ((-r, -1,  r), ( r, -1,  r), ( r, -1, -r), (-r, -1, -r)) # dn
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
    
    def draw(self):
        glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_CULL_FACE)
        glColor3f(1.0, 1.0, 1.0)
        glLoadIdentity()
        
        # Draw the skybox
        num = 0
        for texture in self.texcoords:
            glActiveTexture(GL_TEXTURE0);
            glBindTexture(texture.target, texture.id)
            glEnable(texture.target)
            glTexParameteri(texture.target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(texture.target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0)
            glVertex3f(*self.coords[num][0])
            glTexCoord2f(0.0, 1.0)
            glVertex3f(*self.coords[num][1])
            glTexCoord2f(1.0, 1.0)
            glVertex3f(*self.coords[num][2])
            glTexCoord2f(1.0, 0.0)
            glVertex3f(*self.coords[num][3])
            glEnd()
            num += 1
            
        glPopAttrib()

