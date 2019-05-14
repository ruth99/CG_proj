import sys, time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from textureandcolor import *
from math import pi, cos, sin, sqrt, floor, acos
from random import randint
# from pynput.keyboard import Key, Controller
from pygame import *

# keyboard = Controller()

TITLE = "Polydodge"
WIDTH,HEIGHT = 800,600
SPEED = 24
RADIUS = 60
SIZE = 10
SHRINK_SPEED = 0.65
THICKNESS = 15
ROTATION_SPEED = 0.6

print("this is nice")
print("but this is also wonderful")

def text(string, x, y, size, color=(0,0,0)):
    def linetext(text,x,y,size,color=(0,0,0)):
        @use_color(*color)
        def wrapper():
            glPushMatrix()                          # push and pop the current matrix stack
            glRotate(180,1,0,0)                     #multiply the current matrix by a rotation matrix
            glTranslate(x,y,0)                      # multiply the current matrix by a translation matrix
            default = 120.
            glScale(size/default, size/default, size/default)
            for c in text:
                glutStrokeCharacter(GLUT_STROKE_MONO_ROMAN,ord(c))      # renders a stroke character using OpenGL.
            glPopMatrix()
            return
        return wrapper()
    y = -y
    lines = string.split("\n")
    for i, line in enumerate(lines):
        offset = size+ (size + 10) * i
        linetext(line, x, y-offset, size, color=color)

class App:
    def __init__(self, title):
        self.title = title
        self.frame = 0
        return

    def create_window(self,width, height, fullscreen=False):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(width,height)
        glutCreateWindow(self.title.encode())
        self.width, self.height = width, height
        glEnable(GL_COLOR_MATERIAL)
        glShadeModel(GL_SMOOTH)                         # select flat or smooth shading
        glMatrixMode(GL_PROJECTION)                     # specify pixel arithmetic
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glEnable (GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        return

class Player:
    def __init__(self,radius,size=50,color=(0,0,1)):
        self.radius = radius
        self.color = color
        self.angle = 0
        self.size=size
        return

    def display(self):
        self.angle = self.angle % 360
        glPushMatrix()
        glRotate(self.angle,0,0,1)
        glTranslate(self.radius, 0, 0)

        @use_color(*self.color)
        def circle(radius):
            triangleAmount = 24
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(0,0)
            for i in range(triangleAmount+1):
                glVertex2f((radius * cos(i *  2*pi / triangleAmount)),
                               (radius * sin(i * 2*pi / triangleAmount)))
            glEnd()

        circle(self.size)
        glPopMatrix()

class Shape:
    thickness = THICKNESS
    color = (1,0,0)
    def __init__(self,sides,radius):
        self.radius = radius
        self.sides  = sides
        self.slot   = randint(0,self.sides-1)
        return

    def display(self):
        # draw the shape
        @use_color(*self.color)
        def shape():
            for i in range(0,self.sides):
                if i != self.slot:
                    glPushMatrix()
                    a = 360/self.sides * i
                    glRotate(a,0,0,1)
                    glBegin(GL_QUADS)
                    # some nice trig...
                    glVertex2f(self.radius,0)
                    glVertex2f(self.thickness+self.radius, 0)
                    glVertex2f((self.radius+self.thickness)*cos(2*pi/self.sides),
                               (self.radius+self.thickness)*sin(2*pi/self.sides))
                    glVertex2f(self.radius*cos(2*pi/self.sides), self.radius*sin(2*pi/self.sides))
                    glEnd()
                    glPopMatrix()
            return
        return shape()

    def collision(self,player):
        lowerbound = self.slot*360/self.sides
        upperbound = lowerbound + 360/self.sides
        # modify for size of player sprite (converted to degrees in calculation
        margin = acos((2*self.radius**2-player.size**2)/(2*self.radius**2)) / (2*pi) * 360
        lowerbound += margin
        upperbound -= margin
        return (player.angle < lowerbound or player.angle > upperbound)

class Level:
    def __init__(self,player,shapes):
        self.player = player
        self.shapes = shapes
        self.gameover = False
        self.score = 0
        return

    def update(self,app):
        if self.gameover: return
        p = self.player
        # collisions
        for s in self.shapes:
            if s.radius > p.radius+p.size: break                # if shape is too far out
            elif not s.radius+s.thickness < p.radius-p.size:    # if shape has not already passed
                if s.collision(p):                              # check angle of player to detect collision
                    self.gameover = True
                    return
        # movement
        for s in self.shapes:
            s.radius -= SHRINK_SPEED * (1+app.level.score/20.)
            if s.radius < s.thickness:
                self.shapes.remove(s)
                self.shapes.append(Shape(randint(3,6),WIDTH))
                self.score += 1
        return

    def render(self):
        self.player.display()
        for s in self.shapes:
            s.display()
        return

def main():
    def draw():
        # clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glOrtho(0,WIDTH,HEIGHT,0,-1,1)
        if app.mainmenu:
            # render main menu
            glLineWidth(4)
            text(TITLE.upper(), WIDTH/2-140, HEIGHT/4, 48)
            glLineWidth(2)
            # implement slow flashing text
            frequency = 800
            a = sin((app.frame%frequency)/frequency *2* pi)
            text("Press SPACE to start", WIDTH/2-200, HEIGHT/2, 32,color=(a,a,a))
            text("""\
                Controls:
                SCROLL UP    rotate clockwise
                SCROLL DOWN  rotate anticlockwise""", WIDTH/2-200, 3*HEIGHT/4, 24)
        else:
            # else render level:
            # center matrix
            glPushMatrix()
            glTranslate(WIDTH/2, HEIGHT/2, 0)
            # slowly rotate
            glRotate(app.frame*ROTATION_SPEED,0,0,1)
            # update level
            app.level.update(app)
            # render level
            app.level.render()
            # uncenter matrix
            glPopMatrix()

            # display text
            glLineWidth(4)
            text("Score: {}".format(app.level.score), 4, 4, 24)

            # gameover state...
            if app.level.gameover:
                text("Game over!\nPress SPACE\nto play again", WIDTH/2-120, HEIGHT/2-48, 32)
        glutSwapBuffers()
        app.frame += 1
        return

    def mouse_button(button, state, x, y):
        ''' state 0 is down; state 1 is up '''
        if button == 0: #scroll down
            app.level.player.angle -= SPEED*state
            return
        if button == 2: #scroll up
            app.level.player.angle += SPEED*state
            return
        return

    def keyboard_down(key, x, y):
        ''' Keyboard repeat is enabled by default '''
        ''' x and y represent the mouse position  '''
        if key == b'^[': # ESC key
            glutLeaveMainLoop()
            return
        if key == b' ': # SPACE key
            if app.level.gameover:
                app.level = Level(Player(RADIUS, SIZE),[Shape(randint(3,6),WIDTH),Shape(randint(3,6),WIDTH*1.5)])
            if app.mainmenu:
                app.mainmenu = False
            return
        #check if non-special character
        key = key.decode()
        return

    def keyboard_up(key, x, y):
        return

    def mouse_move(x, y):
        return

    app = App(TITLE)
    app.create_window(WIDTH,HEIGHT)
    glutDisplayFunc( draw )
    glutIdleFunc( draw )
    glutMouseFunc( mouse_button )
    glutKeyboardFunc( keyboard_down )
    glutKeyboardUpFunc( keyboard_up )
    glutPassiveMotionFunc( mouse_move )                # set the motion and passive motion callbacks respectively for the current window.
    app.level_setup = (Player(RADIUS, SIZE),[Shape(randint(3,6),WIDTH),Shape(randint(3,6),WIDTH*1.5)])
    app.level = Level(*app.level_setup)
    app.mainmenu = True
    glClearColor(1, 1, 1, 0)
    glutMainLoop()
    return

if __name__ == "__main__":
    main()

