#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Example showing what can be left out. ESC to quit"""
import demo
import pi3d

DISPLAY = pi3d.Display.create(w=800, h=500, frames_per_second=10, background=(0.1, 0.1, 0.0, 0.0),
                display_config=pi3d.DISPLAY_CONFIG_HIDE_CURSOR | pi3d.DISPLAY_CONFIG_MAXIMIZED, use_glx=True)
shader = pi3d.Shader("uv_flat")
sprite = pi3d.ImageSprite("textures/PATRN.PNG", shader, w=10.0, h=10.0)
mykeys = pi3d.Keyboard()
while DISPLAY.loop_running():
  sprite.draw()
  k = mykeys.read()
  if k == 27:
    mykeys.close()
    DISPLAY.destroy()
    break