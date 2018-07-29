#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Wavefront obj model loading. Material properties set in mtl file.
Uses the import pi3d method to load *everything*
"""
import demo
import pi3d
from math import cos, sin, radians

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100,
                         background=(0.2, 0.4, 0.6, 1), frames_per_second=30)
shader = pi3d.Shader("uv_reflect")
matsh = pi3d.Shader("mat_reflect")
flatsh = pi3d.Shader('uv_flat')
#========================================
# this is a bit of a one off because the texture has transparent parts
# comment out and google to see why it's included here.
from pi3d import opengles, GL_CULL_FACE
opengles.glDisable(GL_CULL_FACE)
#========================================
# load bump and reflection textures
bumptex = pi3d.Texture("textures/floor_nm.jpg")
shinetex = pi3d.Texture("textures/photosphere.jpg")
# load model_loadmodel
mymodel = pi3d.Model(file_string='models/teapot.obj', name='teapot')
mymodel.set_shader(shader)
mymodel.set_normal_shine(bumptex, 0.0, shinetex, 0.4)
# create two material shaded spheres
sphere1 = pi3d.Sphere(radius=0.25, x=2.0)
sphere1.set_draw_details(matsh, [bumptex, shinetex], 4.0, 0.2)
sphere1.set_material((0.4, 0.3, 0.1))
sphere1.set_specular((0.6, 0.6, 0.8))
sphere2 = pi3d.Sphere(radius=0.25, z=2.0)
sphere2.set_draw_details(matsh, [bumptex, shinetex], 4.0, 0.3)
sphere2.set_material((0.2, 0.8, 0.6))
sphere2.set_specular((0.8, 0.8, 1.1))

# environment sphere
mysphere = pi3d.Sphere(radius=400.0, rx=180, ry=180, invert=True)
mysphere.set_draw_details(flatsh, [shinetex])

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
  sphere1.draw()
  sphere2.draw()
  mysphere.draw()
  mymodel.rotateIncY(0.41)
  mymodel.rotateIncZ(0.12)
  mymodel.rotateIncX(0.23)


