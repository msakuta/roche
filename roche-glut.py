#!/usr/bin/python

"""
roche-glut.py

A orbital simulator rendered with PyOpenGL.
"""

import sys, numbers, gc
from math import *
from random import *

try:
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print '''
ERROR: PyOpenGL not installed properly.  
        '''

class vec3(object):
	""" Basic 3-D vector implementation """
	x = 0
	y = 0
	z = 0
	def __init__(self, x=0, y=0, z=0):
		self.x = x
		self.y = y
		self.z = z
	def __neg__(self):
		return vec3(-self.x, -self.y, -self.z)
	def __add__(self, o):
		return vec3(self.x + o.x, self.y + o.y, self.z + o.z)
	def __sub__(self, o):
		return vec3(self.x - o.x, self.y - o.y, self.z - o.z)
	def __mul__(self, s):
		if not isinstance(s, numbers.Number):
			return NotImplemented
		return vec3(self.x * s, self.y * s, self.z * s)
	def __div__(self, s):
		if not isinstance(s, numbers.Number):
			return NotImplemented
		return vec3(self.x / s, self.y / s, self.z / s)
	def __repr__(self):
		return "(" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ")"

	def __getitem__(self,key):
		if key == 0:
			return self.x
		elif key == 1:
			return self.y
		elif key == 2:
			return self.z
		else:
			raise RangeError

	def __setitem__(self,key,value):
		if key == 0:
			self.x = value
		elif key == 1:
			self.y = value
		elif key == 2:
			self.z = value

	def slen(self):
		return self.x ** 2 + self.y ** 2 + self.z ** 2
	def len(self):
		return sqrt(self.slen())

class masspoint(object):
	""" Mass point with position and velocity """
	pos = vec3(0,0,0)
	velo = vec3(0,0,0)
	def __init__(self, pos = vec3(0,0,0), velo = vec3(0,0,0)):
		self.pos = pos
		self.velo = velo
"""	def __cmp__(self, o):
		if self.x < o.x:
			return -1
		elif o.x < self.x:
			return 1
		else:
			return 0"""


points = []
for i in range(50):
	pos = vec3(random() - 0.5, random() - 0.5, random() - 0.5) * 50.
	vertex = masspoint(pos, vec3(0., 0., sqrt(300. / 400.)))

	if vertex.pos.len() < 25:
		vertex.pos.x += 400;
		points.append(vertex)

for i in range(50):
	pos = vec3(random() - 0.5, random() - 0.5, random() - 0.5) * 50.
	vertex = masspoint(pos, vec3(0, 0, sqrt(300. / 600.)))

	if vertex.pos.len() < 25:
		vertex.pos.x += 600;
		points.append(vertex)


def init():
	global quadratic
	glClearColor(0.0, 0.0, 0.0, 0.0)
	glClearDepth(1.0)
	glShadeModel(GL_SMOOTH)
	quadratic = gluNewQuadric()
	gluQuadricNormals(quadratic, GLU_SMOOTH)
	gluQuadricTexture(quadratic, GL_TRUE)
	glEnable(GL_CULL_FACE)
	glEnable(GL_DEPTH_TEST)

dist = 1000
phi = 30
theta = 30

def getAccel(i,v):
	accel = v * (-300. / (v.len() ** 3))
	for p in points:
		if i != p:
			delta = v - p.pos
			accel += delta * (-0.01 / (delta.len() ** 3))
	return accel

def euler(deltaTime):
	for p in points:
		v = p.pos
		norm = v.len()
		p.velo += getAccel(p, v) * deltaTime
		p.pos += p.velo * deltaTime

def rg2(deltaTime):
	for p in points:
		v = p.pos
		norm = v.len()
		accel = getAccel(p, v)
		dvelo = accel * deltaTime * 0.5
		vec0 = v + p.velo * deltaTime / 2.
		accel1 = getAccel(p, vec0)
		velo1 = p.velo + dvelo
		p.velo += accel1 * deltaTime
		p.pos += velo1 * deltaTime


method = rg2

def display():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	glLoadIdentity()
	# viewing transformation
	lookpos = vec3(cos(phi * pi / 180) * cos(theta * pi / 180), sin(theta * pi / 180), sin(phi * pi / 180) * cos(theta * pi / 180)) * dist
	gluLookAt(lookpos[0], lookpos[1], lookpos[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

	glBegin(GL_LINES)
	glColor3f (1.0, 0.0, 0.0)
	glVertex3d(-1000, 0, 0)
	glVertex3d( 1000, 0, 0)
	glColor3f (0.0, 1.0, 0.0)
	glVertex3d(0, -1000, 0)
	glVertex3d(0,  1000, 0)
	glColor3f (0.0, 0.0, 1.0)
	glVertex3d(0, 0, -1000)
	glVertex3d(0, 0,  1000)
	glEnd()

	deltaTime = 2
	method(deltaTime)

	glColor3f (1.0, 1.0, 1.0)
	glBegin(GL_POINTS)
	for p in points:
		v = p.pos
		glVertex3d(v.x, v.y, v.z)
	glEnd()

	glPushAttrib(GL_LIGHTING_BIT)
	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	glLightfv(GL_LIGHT0, GL_POSITION, [1., 2., 1., 0.]);
	glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.]);
	glLightfv(GL_LIGHT0, GL_DIFFUSE, [1., 1., 1., 0]);
	glLightfv(GL_LIGHT0, GL_SPECULAR, [0, 0, 1, 0]);
	gluSphere(quadratic, 200, 20, 20)
	glPopAttrib()

	glFlush()

	glutPostRedisplay()
	print gc.get_count(), gc.garbage

mousestate = False
mousepos = [0,0]

def mouse(button, state, x, y):
	if state:
		mousestate = True
	else:
		mousestate = False
	mousepos[0] = x
	mousepos[1] = y

def motion(x, y):
	global phi, theta
	theta -= mousepos[1] - y
	if theta < -90:
		theta = -90
	if 90 < theta:
		theta = 90
	mousepos[1] = y
	phi -= mousepos[0] - x
	mousepos[0] = x

def keyboard(key, x, y):
	global dist
	if key == '+':
		dist /= 1.1
	if key == '-':
		dist *= 1.1
	if key == chr(27):
		sys.exit(0)

def reshape (w, h):
	glViewport(0, 0, w, h)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glFrustum(-1.0, 1.0, -1.0, 1.0, 1.5, 5000.0)
	glMatrixMode(GL_MODELVIEW)

glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(500, 500)
glutInitWindowPosition(100, 100)
glutCreateWindow('Orbit Simulator')
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutMouseFunc(mouse)
glutMotionFunc(motion)
glutKeyboardFunc(keyboard)
glutMainLoop()
