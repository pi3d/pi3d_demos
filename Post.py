#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

""" PostProcess. The rendered scene can be processed by the
shader passed to the PostProcess class. The PostProcess.draw() method can
have a dict of unif keys and variable passed to it which can then be used
by the shader to create dynamic effects

PostProcess also allows a scale factor to be used. This can cut down render
time by using glScissor to only run the fragment shader on a small part of
the screen (seems to fail with scale < 0.3 for some reason) To maintain
the same perspective the camera scale (as used by Camera.__init__) and the
texture scale (as used by PostProcess.__init__) need to be the same.

There is also a facility in PostProcess (inherited from OffScreenTexture)
that allow the clearing on start() to be toggled on and off. Any key
apart from p or escape will show this effect.
"""
import math, random, time

import demo
import pi3d

print("shapes change with mouse movement!")
# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100, w=800, h=800, frames_per_second=40,
          mouse=True)
DISPLAY.set_background(0.4, 0.6, 0.8, 1.0)      # r,g,b,alpha

persp_cam = pi3d.Camera(scale=0.5) # default instance camera perspecive view

#setup textures, light position and initial model position
pi3d.Light((0, 5, 0))
#create shaders
shader = pi3d.Shader("star")
flatsh = pi3d.Shader("uv_flat")
post = pi3d.PostProcess(camera=persp_cam, scale=0.5)

#Create textures
shapeimg = pi3d.Texture("textures/straw1.jpg")
shapebump = pi3d.Texture("textures/floor_nm.jpg", True)

#Create shape
myshape = pi3d.MergeShape(camera=persp_cam) #specify perspective view
asphere = pi3d.Sphere(sides=32, slices=32)
myshape.radialCopy(asphere, step=72)
myshape.position(0.0, 0.0, 5.0)
myshape.set_draw_details(shader, [shapeimg], 8.0, 0.1)

mysprite = pi3d.Sprite(w=10.0, h=10.0, camera=persp_cam)
mysprite.position(0.0, 0.0, 15.0)
mysprite.set_draw_details(flatsh, [shapebump])

# Fetch key presses.
mykeys = pi3d.Keyboard()
tm = 0.0
dt = 0.02
sc = 0.0
ds = 0.001
x = 0.0
dx = 0.001
clear = True
# Display scene and rotate shape
n = 0
start = time.time()
while DISPLAY.loop_running():
  tm = tm + dt
  sc = (sc + ds) % 10.0
  myshape.set_custom_data(48, [tm, sc, -0.5 * sc]) 
  # NB NB for pi3d prior to v1.15 the array index would be 48 rather than 16
  post.start_capture(clear=clear)
  # 1. drawing objects now renders to an offscreen texture ####################

  mysprite.draw()
  myshape.draw()

  post.end_capture()
  # 2. drawing now back to screen. The texture can now be used by post.draw()

  # 3. redraw these two objects applying a shader effect ###############
  x = (x + dx) % 5.0
  post.draw({48:(2.0 + x), 49:0.0, 50:0.0})

  mx, my = DISPLAY.mouse.position()
  myshape.scale(1.0 + mx/1000.0, 1.0 + my/1000.0, 1.0 + mx/1000.0)
  myshape.rotateIncY(0.6471)
  myshape.rotateIncX(0.0613)
  n += 1

  k = mykeys.read()
  if k==ord('p'): # take screen shot
    pi3d.screenshot("post.jpg")
  elif k==27: # escape
    mykeys.close()
    DISPLAY.destroy()
    break
  elif k > -1: # any other key toggle OffScreenTexture clear
    clear = not clear
print("{:.1f}fps".format(n / (time.time() - start)))