#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Example showing use of FixedString. ESC to quit

FixedString should be faster for rendering large quantities of text as
it only requires two triangles for the whole text rather than two triangles
for each letter"""
import demo
import pi3d

DISPLAY = pi3d.Display.create(x=150, y=150)
shader = pi3d.Shader("uv_flat")
pi3d.Camera(is_3d=False)
sprite = pi3d.FixedString('fonts/FreeSans.ttf', '''Pi3D is a Python module that aims to greatly
simplify writing 3D in Python whilst giving
access to the power of the Raspberry Pi GPU.
It enables both 3D and 2D rendering and aims
to provide a host of exciting commands to load
in textured/animated models, create fractal
landscapes, shaders and much more.''', 
          shader=shader, background_color = (250, 140, 60, 240))
mykeys = pi3d.Keyboard()
while DISPLAY.loop_running():
  sprite.draw()
  if mykeys.read() == 27:
    mykeys.close()
    DISPLAY.destroy()
    break
