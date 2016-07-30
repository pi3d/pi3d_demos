#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Example showing what can be left out. ESC to quit"""
import demo
import pi3d
import numpy as np
import picamera
import picamera.array
import threading
import time
from math import cos, sin, radians


npa = None
new_pic = False

def get_pics():
  global npa, new_pic
  with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as output:
      camera.resolution = (320, 240)
      while True:
        output.truncate(0)
        camera.capture(output, 'rgb')
        if npa is None:
          npa = np.zeros(output.array.shape[:2] + (4,), dtype=np.uint8)
          npa[:,:,3] = 255
        npa[:,:,0:3] = output.array
        new_pic = True
        time.sleep(0.05)

t = threading.Thread(target=get_pics)
t.daemon = True
t.start()

while not new_pic:
    time.sleep(0.1)


# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100,
                         background=(0.2, 0.4, 0.6, 1))
shader = pi3d.Shader("uv_reflect")
flatsh = pi3d.Shader('uv_flat')
#========================================
# this is a bit of a one off because the texture has transparent parts
# comment out and google to see why it's included here.
from pi3d import opengles, GL_CULL_FACE
opengles.glDisable(GL_CULL_FACE)
#========================================
# load bump and reflection textures
bumptex = pi3d.Texture("textures/floor_nm.jpg")
shinetex = pi3d.Texture(npa)
# load model_loadmodel
mymodel = pi3d.Model(file_string='models/teapot.obj', name='teapot')
mymodel.set_shader(shader)
mymodel.set_normal_shine(bumptex, 0.0, shinetex, 0.7)

mysphere = pi3d.Sphere(radius=400.0, rx=180, ry=180, invert=True)
mysphere.set_draw_details(flatsh, [shinetex], vmult=3.0, umult=3.0)

# Fetch key presses
mykeys = pi3d.Keyboard()
mymouse = pi3d.Mouse(restrict=False)
mymouse.start()

omx, omy = mymouse.position()

CAMERA = pi3d.Camera.instance()

dist = 4.0
rot = 0.0
tilt = 0.0

while DISPLAY.loop_running():
  k = mykeys.read()
  if k >-1:
    if k==ord('w'):
      dist += 0.02
    if k==ord('s'):
      dist -= 0.02
    elif k==27:
      mykeys.close()
      DISPLAY.destroy()
      break

  if new_pic:
    shinetex.update_ndarray(npa)
    new_pic = False

  mx, my = mymouse.position()
  rot -= (mx - omx)*0.4
  tilt += (my - omy)*0.4
  omx = mx
  omy = my
  CAMERA.reset()
  CAMERA.rotate(-tilt, rot, 0)
  CAMERA.position((dist * sin(radians(rot)) * cos(radians(tilt)), 
                   dist * sin(radians(tilt)), 
                   -dist * cos(radians(rot)) * cos(radians(tilt))))
  
  mymodel.draw()
  mysphere.draw()
  mymodel.rotateIncY(0.41)
  mymodel.rotateIncZ(0.12)
  mymodel.rotateIncX(0.23)


