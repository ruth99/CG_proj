## texture loading
import pygame.image
from OpenGL.GL import *

def loadPNG(path):
    with open(path, 'rb') as f:
        data = f.read()
    print(len(data))
    return data

def load_texture(path):
    textureSurface = pygame.image.load(path)
    data = pygame.image.tostring(textureSurface, "RGBA", 1)
    #data = loadPNG(path)
    width = textureSurface.get_width()
    height = textureSurface.get_height()
    return (width, height, data)

def use_texture(texture):  #this is a decorator
    def func_wrapper(drawfunc):
        def a(*args, **kwargs):
            width, height, textureData = texture

            glEnable(GL_TEXTURE_2D)
            texid = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texid)                                         # bind a named texture to a texturing target
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                         0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)                #set texture parameters
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)

            glColor3f(1., 1., 1.)
            drawfunc(*args, **kwargs)
            glDisable(GL_TEXTURE_2D)
        return a
    return func_wrapper

def use_color(r, g, b):  #this is a decorator
    def func_wrapper(drawfunc):
        def a(*args, **kwargs):
            glColor3f(r, g, b)
            drawfunc(*args, **kwargs)
            glColor3f(1., 1., 1.)
        return a
    return func_wrapper
