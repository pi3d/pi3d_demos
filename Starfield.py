#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Use of points by using set_point_size() to a non-zero value. This example
uses a comprehensive star database https://github.com/astronexus/HYG-Database
thanks to David Nash. It will take quite a few seconds to load the data
and parse it into a numpy array.
"""
print("""To turn the camera use the mouse:
-- W increases forward speed by 5%
-- S decreases forward speed and eventually reverses
-- space stops dead if you are moving. If you have stopped pressing space
again will return you to the middle of the solar system. Repeatedly pressing
space will toggle between the middle and 1.1 parsecs away. The near plane
is one parsec from the camera so stars nearer than that will dissapear.
-- any other key will report info on whichever named star is nearest in
line with the camera direction. The data has the constellation, the Harvard
catalogue ref, the name from Gliese Catalog of Nearby Stars, the distance
and the current speed as multiples of light speed.
""")

import demo
import pi3d
import numpy as np
import time
import threading

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=50, y=50, near=0.05, far=100000, frames_per_second=20, samples=4) #note big far and small near plane values
DISPLAY.set_background(0,0,0,1)    	# black!
CAM = pi3d.Camera()
CAM2D = pi3d.Camera(is_3d=False)
flatsh = pi3d.Shader("uv_flat")
matsh = pi3d.Shader("mat_flat")

target = pi3d.Sprite(camera=CAM2D, z=5.0, w=50, h=50)
target.set_draw_details(flatsh, [pi3d.Texture("textures/target.png")])

import stars # tucked away in another file for tidyness!
s = stars.Stars()

font = pi3d.Font('fonts/NotoSans-Regular.ttf')
name_loc = s.v[list(s.names)] # this will be a view of the full array, only for named stars
label = pi3d.String(font=font, string='Sol', y=-250, is_3d=False, camera=CAM2D)
label.set_shader(flatsh)

t = threading.Thread(target=s.select_visible) # run in infinite loop
t.daemon = True
t.start()

while not s.ready: # to ensure stars set up first time in select_visible
  time.sleep(0.1)

''' constelation lines '''
orion = [231, 44288, 52501, 100413, 52501, 42572, 62904, 55898, 71408,
         59549, 17025, 5088, 42572, 5088, 17025, 81378,14265, 14597, 14265,
         81378, 51101, 76177]
orion_line = pi3d.Lines(vertices=s.v[orion,:3])
orion_line.set_shader(matsh)
ursamajor = [2982, 5454, 2934, 3178, 2982, 3144, 3324, 4284]
ursamajor_line = pi3d.Lines(vertices=s.v[ursamajor,:3], material=(0.0, 0.2, 0.9))
ursamajor_line.set_shader(matsh)
pi = [0, 667, 5187, 667, 31882, 7980, 31882, 9285]
pi_line = pi3d.Lines(vertices=s.v[pi,:3], material=(0.87, 0.0, 0.67))
pi_line.set_shader(matsh)

import starsystem as sm # tucked away in another file for tidyness!
near_system = sm.StarSystem(sm.systems[0][0], sm.systems[0][1], sm.systems[0][2], s.v)

mymouse = pi3d.Mouse(restrict = False)
mymouse.start()
rot = 0.0
tilt = 0.0
step = [0.0, 0.0, 0.0]

# Fetch key presses
mykeys = pi3d.Keyboard()
# Display scene
fr = 1
rec = False
while DISPLAY.loop_running():
  mx, my = mymouse.position()
  rot = - mx * 0.2
  tilt = my * 0.2
  s.xm, s.ym, s.zm = CAM.relocate(rot, tilt, point=[s.xm, s.ym, s.zm], distance=step)

  s.draw()
  lbla = label.alpha()
  if lbla > 0.05:
    label.draw()
    orion_line.draw()
    ursamajor_line.draw()
    pi_line.draw()
    label.set_alpha(lbla * 0.98)
    orion_line.set_alpha(lbla * 0.5)
    ursamajor_line.set_alpha(lbla * 0.5)
    pi_line.set_alpha(lbla * 0.5)

  sublight = abs(step[0]) < 0.002
  if sublight:
    near_system.draw()
    
  target.draw()
  if s.ready:
    s.re_init()

  k = mykeys.read()
  if k > -1:
    if k == ord('p'):
      rec = not rec
    elif k == ord('w'):
      step = [i + i * 0.05 for i in step] if step[0] >= 0.001 else [0.001, 0.001 , 0.001]
    elif k == ord('s'):
      step = [i - abs(i) * 0.05 for i in step] if abs(step[0]) >= 0.001 else [-0.001, -0.001, -0.001]
    elif k == 27:
      mykeys.close()
      DISPLAY.stop()
      break
    else: #any other key
      if k == ord(' '): # stop and load nearest 'system'
        r_loc = s.v[[systm[0] for systm in sm.systems],0:3] - [s.xm, s.ym, s.zm] # dist systems rel cam
        r_dist = (r_loc[:,0] ** 2 + r_loc[:,1] ** 2 + r_loc[:,2] ** 2).reshape(-1, 1) # euclidean dist
        n = np.argmin(r_dist) # this one's nearest
        if r_dist[n] < 6.0:
          near_system.visible = True
          if near_system.star_ref != n:
            near_system.change_details(sm.systems[n][0], sm.systems[n][1], sm.systems[n][2], s.v)
          if not sublight:
            s.xm, s.ym, s.zm = s.v[sm.systems[n][0],0:3] + [0.2, 0.0, -2.0]
        else:
          near_system.visible = False
        step = [0.0, 0.0, 0.0]
      r_loc = name_loc[:,0:3] - [s.xm, s.ym, s.zm] # array of named stars' position rel to camera
      # calculate the euclidean distance to normalize the array to unti vectors...
      r_dist = ((r_loc[:,0] ** 2 + r_loc[:,1] ** 2 + r_loc[:,2] ** 2) ** 0.5).reshape(-1, 1)
      # choose the vector that most nearly matches the direction the camera is pointing...
      n = np.argmax(np.dot(r_loc / r_dist, CAM.get_direction()))
      # use n to look up the index held in the 8th column of the name_loc
      label = pi3d.String(font=font, string='{} {:7.1f}l.yrs v={:.1E}c'.format(
              s.names[int(name_loc[n, 7])], r_dist[n,0] * 3.262, step[0] * 2057000000.0), # parsec to c
              y=-250, is_3d=False, camera=CAM2D)
      label.set_shader(flatsh)
      label.set_alpha(1.5)
      orion_line.set_alpha(0.5)
      ursamajor_line.set_alpha(0.5)
  #if rec:
  #  pi3d.screenshot('/home/patrick/Downloads/scr_caps_pi3d/scr_caps/f{:05d}.jpg'.format(fr))
  #  fr += 1
