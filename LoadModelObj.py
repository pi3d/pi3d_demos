#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Wavefront obj model loading. Material properties set in mtl file.
Uses the import pi3d method to load *everything*
"""
import demo
import pi3d
# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100,
                         background=(0.2, 0.4, 0.6, 1), frames_per_second=30)
shader = pi3d.Shader("uv_reflect")
#========================================
# this is a bit of a one off because the texture has transparent parts
# comment out and google to see why it's included here.
pi3d.opengles.glDisable(pi3d.GL_CULL_FACE)
#========================================
# load bump and reflection textures
bumptex = pi3d.Texture("textures/floor_nm.jpg")
shinetex = pi3d.Texture("textures/stars.jpg")
# load model_loadmodel
mymodel = pi3d.Model(file_string='models/teapot.obj', name='teapot', z=4.0)
mymodel.set_shader(shader)
mymodel.set_normal_shine(bumptex, 16.0, shinetex, 0.5)
# Fetch key presses
mykeys = pi3d.Keyboard()

while DISPLAY.loop_running():
  mymodel.draw()
  mymodel.rotateIncY(0.41)
  mymodel.rotateIncZ(0.12)
  mymodel.rotateIncX(0.23)

  k = mykeys.read()
  if k >-1:
    if k==112:
      pi3d.screenshot('teapot.jpg')
    elif k==27:
      mykeys.close()
      DISPLAY.destroy()
      break
