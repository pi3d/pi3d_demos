#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" An example of making objects change shape using Buffer.re_init().
It shows how a subset of vertices can be altered
"""
from math import sin, cos, radians
from time import time
import random

import demo
import pi3d

DISPLAY = pi3d.Display.create(x=50, y=50, frames_per_second=20)
shader = pi3d.Shader("uv_reflect")
tex = pi3d.Texture("textures/metalhull.jpg")
bump = pi3d.Texture("textures/rocktile2.jpg")
shine = pi3d.Texture("textures/stars2.jpg")

ice = pi3d.Sphere(slices=32, sides=32)
ice.set_draw_details(shader, [tex, bump, shine], 1.0, 0.8)

tm = time()
dgrow = 0.05 # time between 'growing' the shapes
nextgrow = 0.0 # time to do next growing
dnormal = 0.5 # time between recalculating all normals
nextnormal = 0.0 # time to do next normals
camRad = 4.0 # radius of camera position
mouserot = 0.0 # rotation of camera
tilt = 5.0 # tilt of camera

#key presses
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()
omx, omy = mymouse.position()

mykeys = pi3d.Keyboard()
CAMERA = pi3d.Camera.instance()

# main display loop
while DISPLAY.loop_running():
  tm = time()
  mx, my = mymouse.position() # camera can move around object with mouse move
  mouserot -= (mx-omx)*0.2
  tilt -= (my-omy)*0.1
  omx=mx
  omy=my
  CAMERA.reset()
  CAMERA.rotate(-tilt, mouserot, 0)
  CAMERA.position((camRad * sin(radians(mouserot)) * cos(radians(tilt)), 
                   camRad * sin(radians(tilt)), 
                   -camRad * cos(radians(mouserot)) * cos(radians(tilt))))

  ice.draw()

  if tm  > nextgrow: # can't do this inside the tetra for loop otherwise only first one updated
    b = ice.buf[0] #alias to tidy code. NB there may be issues with multi Buffer Shapes
    n = len(b.array_buffer)
    f = random.randint(0, n-5) #from 
    e = min(random.randint(f+1, n-1), f + 50) #end
    vmod = []
    nmod = []
    tmod = []
    for j in range(f, e): # nb only
      vmod.append(tuple(b.array_buffer[j,i] * (0.995 + random.random() / 50.0) for i in range(0,3)))
      tmod.append(tuple(b.array_buffer[j,i] * (0.99 + random.random() / 50.0) for i in range(6,8)))
    b.re_init(pts=vmod, texcoords=tmod, offset=f)
    nextgrow += dgrow

  if tm > nextnormal:
    b = ice.buf[0] #alias to tidy code
    for i in range(33): #number of slices + 1
      b.array_buffer[33*i + 32,0:3] = b.array_buffer[33*i,0:3] #attempt to re-align edges of mesh
    b.normals = b.calc_normals()
    b.re_init(normals = b.normals)
    nextnormal = tm + dnormal

  if mykeys.read() == 27:
    mykeys.close()
    mymouse.stop()
    DISPLAY.destroy()
    break
