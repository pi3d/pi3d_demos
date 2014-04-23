#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" PhotoSphere image mapped to inverted sphere. NB the image has to be
flipped to stop mirroring, this will put it upside down so it needs to be
rotated!
"""
import demo
import pi3d

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=50, y=50)

shader = pi3d.Shader('uv_flat')
#========================================
tex = pi3d.Texture('textures/photosphere.jpg', flip=True)
mysphere = pi3d.Sphere(radius=400.0, rx=180, invert=True)
mysphere.set_draw_details(shader, [tex])

rot = 0.0
tilt = 0.0

# Fetch key presses
mykeys = pi3d.Keyboard()
mymouse = pi3d.Mouse(restrict=False)
mymouse.start()

omx, omy = mymouse.position()

CAMERA = pi3d.Camera.instance()

# Display scene and rotate cuboid
while DISPLAY.loop_running():

  CAMERA.reset()
  CAMERA.rotate(tilt, 0, 0)
  CAMERA.rotate(0, rot, 0)

  mysphere.draw()

  mx, my = mymouse.position()

  rot -= (mx - omx)*0.4
  tilt += (my - omy)*0.4
  omx = mx
  omy = my

  #Press ESCAPE to terminate
  k = mykeys.read()
  if k >-1:
    if k==112:  #key P
      pi3d.screenshot('envsphere.jpg')
    elif k==27:    #Escape key
      mykeys.close()
      mymouse.stop()
      DISPLAY.stop()
      break
    else:
      print(k)


