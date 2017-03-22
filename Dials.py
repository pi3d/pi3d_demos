#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Simplest possible demo showing dials with pi3d
"""
import demo
import pi3d
import random

DISPLAY = pi3d.Display.create(w=400, h=400, frames_per_second=20.0,
                              background=(0.5, 0.5, 0.5, 0.5))
# Two dials using ImageSprite for background and needle
flatsh = pi3d.Shader("uv_flat")
cam = pi3d.Camera(is_3d=False)
dials = [pi3d.ImageSprite('textures/{}.png'.format(f), flatsh, camera=cam, 
                          w=180, h=180, x=-100 + i * 200.0, y=100.0, z=5.0)
         for i, f in enumerate(('airspeed_indicator', 'altimeter'))]
needle = pi3d.ImageSprite("textures/instrument_needle.png", flatsh, camera=cam,
                          w=180, h=180, x=-100, y=100.0, z=1.0)
dials[0].value = 50.0 # python can just add properties to instances of ojbects!
dials[1].value = 120.0

# A simple dial using just a pointer. The colour changes and it has 3D shading
# despite using the 2D camera
simple_dial = pi3d.Tetrahedron(corners=((-10,-10,10), (10,-10,10), (0,50,10), (0,0,0)), camera=cam,
                          x=-100, y=-100, z=1.0)
simple_dial.set_shader(pi3d.Shader("mat_light"))
simple_dial.value = 75.0
keys = pi3d.Keyboard()

while DISPLAY.loop_running():
  # ImageSprite dials
  for i, d in enumerate(dials):
    d.draw()
    d.value += random.random() * 10.0 - 4.9
    needle.rotateToZ(d.value)
    needle.positionX(-100.0 + i * 200.0)
    needle.draw()
  # simple dial
  simple_dial.value += random.random() * 5.0 - 2.0
  redgreen = (simple_dial.value / 360.0) % 1.0
  simple_dial.set_material((1.0 - redgreen, redgreen, 0.0))
  simple_dial.rotateToZ(simple_dial.value)
  simple_dial.draw()
  if keys.read() == 27: # ESC key will stop
    break
