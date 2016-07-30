#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import pi3d
import numpy as np
import picamera
import picamera.array
import threading
import time

npa = None # this is the array for the camera to fill
new_pic = False # this is the flag to signal when array refilled

def get_pics():
  # function to run in thread
  global npa, new_pic
  with picamera.PiCamera() as camera:
    camera.resolution = (240, 240)
    with picamera.array.PiRGBArray(camera) as output:
      while True: # loop for ever
        output.truncate(0)
        camera.capture(output, 'rgb')
        if npa is None: # do this once only
          npa = np.zeros(output.array.shape[:2] + (4,), dtype=np.uint8)
          npa[:,:,3] = 255 # fill alpha value
        npa[:,:,0:3] = output.array # copy in rgb bytes
        new_pic = True
        time.sleep(0.05)

t = threading.Thread(target=get_pics) # set up and start capture thread
t.daemon = True
t.start()

while not new_pic: # wait for array to be filled first time
    time.sleep(0.1)

########################################################################
DISPLAY = pi3d.Display.create(x=150, y=150, frames_per_second=30)
shader = pi3d.Shader("shaders/night_vision")
CAMERA = pi3d.Camera(is_3d=False)
tex = pi3d.Texture(npa)
rim = pi3d.Texture('textures/snipermode.png')
noise = pi3d.Texture('textures/Roof.png')
sprite = pi3d.Sprite(w=DISPLAY.height * tex.ix / tex.iy, h=DISPLAY.height, z=5.0)
sprite.set_draw_details(shader, [tex, rim, noise])

mykeys = pi3d.Keyboard()

lum_threshold = 0.2
lum_amplification = 4.0

while DISPLAY.loop_running():
  if new_pic:
    tex.update_ndarray(npa)
    new_pic = False
  sprite.set_custom_data(48, [time.time(), lum_threshold, lum_amplification])
  sprite.draw()

  if mykeys.read() == 27:
    mykeys.close()
    DISPLAY.destroy()
    break
