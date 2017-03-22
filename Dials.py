#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Simplest possible demo showing dials with pi3d
"""
import demo
import pi3d
import random

DISPLAY = pi3d.Display.create(w=400, h=200, frames_per_second=20.0)
flatsh = pi3d.Shader("uv_flat")
cam = pi3d.Camera(is_3d=False)
dials = [pi3d.ImageSprite('textures/{}.png'.format(f), flatsh, camera=cam, 
                          w=180, h=180, x=-100 + i * 200.0, z=5.0)
         for i, f in enumerate(('airspeed_indicator', 'altimeter'))]
needle = pi3d.ImageSprite("textures/instrument_needle.png", flatsh, camera=cam,
                          w=180, h=180, x=-100, z=1.0)
dials[0].value = 50.0
dials[1].value = 120.0
keys = pi3d.Keyboard()
while DISPLAY.loop_running():
  for i, d in enumerate(dials):
    d.draw()
    d.value += random.random() * 10.0 - 4.9
    needle.rotateToZ(d.value)
    needle.positionX(-100.0 + i * 200.0)
    needle.draw()
  if keys.read() == 27: # ESC key will stop
    break
