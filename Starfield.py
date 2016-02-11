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

from six.moves import xrange

def bv2rgb(bv):
  ''' convert blue value to rgb approximations. See
  http://stackoverflow.com/questions/21977786/ with thanks to @Spektre
  '''
  if bv < -0.4: bv = -0.4
  if bv > 2.0: bv = 2.0
  if bv >= -0.40 and bv < 0.00:
    t = (bv + 0.40) / (0.00 + 0.40)
    r = 0.61 + 0.11 * t + 0.1 * t * t
    g = 0.70 + 0.07 * t + 0.1 * t * t
    b = 1.0
  elif bv >= 0.00 and bv < 0.40:
    t = (bv - 0.00) / (0.40 - 0.00)
    r = 0.83 + (0.17 * t)
    g = 0.87 + (0.11 * t)
    b = 1.0
  elif bv >= 0.40 and bv < 1.60:
    t = (bv - 0.40) / (1.60 - 0.40)
    r = 1.0
    g = 0.98 - 0.16 * t
  else:
    t = (bv - 1.60) / (2.00 - 1.60)
    r = 1.0
    g = 0.82 - 0.5 * t * t
  if bv >= 0.40 and bv < 1.50:
    t = (bv - 0.40) / (1.50 - 0.40)
    b = 1.00 - 0.47 * t + 0.1 * t * t
  elif bv >= 1.50 and bv < 1.951:
    t = (bv - 1.50) / (1.94 - 1.50)
    b = 0.63 - 0.6 * t * t
  else:
    b = 0.0
  return [r, g, b]


def select_visible():
  ''' this takes a subset of the total star array v and loads the locations
  into verts, the rgb values into norms, the luminance into texs[:,0] and
  the index number (for looking up the description) into texs[:,1]
    The selection is done on the basis of luminance divided by cartesian
  distance from the camera. The number selected is checked so that the
  size updated back to the Buffer.array_buffer is the same.
    The function is run the first time as a one off to create the initial
  stars object. Subsequently it runs in an infinite while loop in its own
  thread, checking every 2s and signalling to the main loop using the
  global 'ready' flag.
  '''
  global ready, v, xm, ym, zm, verts, norms, texs, stars
  while True:
    indx = np.where(v[:,6] / ((v[:,0] - xm) ** 2 + (v[:,1] - ym)  ** 2 + (v[:,2] - zm) ** 2) > 0.002)
    if verts is None:
      verts = np.zeros((len(indx[0]), 3), dtype='float32')
      norms = np.zeros((len(indx[0]), 3), dtype='float32')
      texs = np.zeros((len(indx[0]), 2), dtype='float32')
    nv = min(len(verts), len(indx[0]))
    verts[:nv] = v[indx[0],0:3][:nv]
    norms[:nv] = v[indx[0],3:6][:nv]
    texs[:nv] = v[indx[0],6:8][:nv]
    if stars is not None:
      ready = True
    else:
      return # do first time blocking execution
    time.sleep(2.0)


# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=50, y=50, far=100000, frames_per_second=20) #note big far plane value
DISPLAY.set_background(0,0,0,1)    	# black!
CAM = pi3d.Camera()
CAM2D = pi3d.Camera(is_3d=False)
flatsh = pi3d.Shader("uv_flat")
starsh = pi3d.Shader("shaders/star_point") #shader uses rgb and luninosity

earthimg = pi3d.Texture("textures/world_map.jpg")
# Load shapes
mysphere = pi3d.Sphere(radius=2, slices=24, sides=24,
                  name="earth", x=10, y=-5, z=180)
mysphere.set_draw_details(flatsh, [earthimg])
target = pi3d.Sprite(camera=CAM2D, z=5.0, w=50, h=50)
target.set_draw_details(flatsh, [pi3d.Texture("textures/target.png")])

v = []
names = {} # most stars are unamed so it is more efficient to use a dictionary
with open('models/hygdata001.csv','r') as f: # read the data from the file
  for i,l in enumerate(f.readlines()):
    ln = l.split(',')
    if ln[0] > '':
      names[i] = '' + ln[5] + ' ' + ln[0] # named star, prefix with constellation
    if ln[1] == '': # no blue value, use a mid
      ln[1] = '0.6'
    v.append([float(ln[2]), float(ln[4]), float(ln[3])] + # z and y swapped to OpenGL orientation.
             bv2rgb(float(ln[1])) +
             [float(vi) for vi in ln[6:7]] + [1.0 * i]) # last value is for index to names 

v = np.array(v, dtype='float32') # and convert to ndarray
font = pi3d.Font('fonts/FreeSans.ttf')
name_loc = v[list(names)] # this will be a view of the full array, only for named stars
label = pi3d.String(font=font, string='Sol', y=-250, is_3d=False, camera=CAM2D)
label.set_shader(flatsh)
xm, ym, zm = 0.0, 0.0, -1.1 # this is 1.1 parsecs away! Too close and it's inside the near plane!
verts, norms, texs = None, None, None
stars = None
ready = False
select_visible() # initial run, one off
stars = pi3d.Points(vertices=verts, normals=norms, tex_coords=texs, point_size=15)
stars.set_shader(starsh)

t = threading.Thread(target=select_visible) # run in infinite loop
t.daemon = True
t.start()

while stars is None: # to ensure stars set up first time in select_visible
  time.sleep(0.1)

mymouse = pi3d.Mouse(restrict = False)
mymouse.start()
rot = 0.0
tilt = 0.0
step = [0.0, 0.0, 0.0]

# Fetch key presses
mykeys = pi3d.Keyboard()
# Display scene
while DISPLAY.loop_running():
  mx, my = mymouse.position()
  rot = - mx * 0.2
  tilt = my * 0.2
  xm, ym, zm = CAM.relocate(rot, tilt, point=[xm, ym, zm], distance=step)

  stars.draw()
  lbla = label.alpha()
  if lbla > 0.1:
    label.draw()
    label.set_alpha(lbla * 0.99)
  target.draw()
  if ready:
    stars.re_init(pts=verts, normals=norms, texcoords=texs) # have to do this in main thread
    ready = False

  k = mykeys.read()
  if k > -1:
    if k == 112:
      pi3d.screenshot("starfield.jpg")
    elif k == ord('w'):
      step = [i + i * 0.05 for i in step] if step[0] >= 0.001 else [0.001, 0.001 , 0.001]
    elif k == ord('s'):
      step = [i - abs(i) * 0.05 for i in step] if abs(step[0]) >= 0.001 else [-0.001, -0.001, -0.001]
    elif k == 27:
      mykeys.close()
      DISPLAY.stop()
      break
    else: #any other key
      if k == ord(' '):
        if step == [0.0, 0.0, 0.0]: # already stopped
          if (xm, ym, zm) == (0.0, 0.0, 0.0): # at location of Sol, move away to be able to see it
            xm, ym, zm = 0.0, 0.0, -1.1
          else:
            xm, ym, zm = 0.0, 0.0, 0.0
        step = [0.0, 0.0, 0.0]
      r_loc = name_loc[:,0:3] - [xm, ym, zm] # array of named stars' position rel to camera
      # calculate the euclidean distance to normalize the array to unti vectors...
      r_dist = ((r_loc[:,0] ** 2 + r_loc[:,1] ** 2 + r_loc[:,2] ** 2) ** 0.5).reshape(-1, 1)
      # choose the vector that most nearly matches the direction the camera is pointing...
      n = np.argmax(np.dot(r_loc / r_dist, CAM.mtrx[0:3,3]))
      # use n to look up the index held in the 8th column of the name_loc
      label = pi3d.String(font=font, string='{} {:7.1f}l.yrs v={:.1E}c'.format(
              names[int(name_loc[n, 7])], r_dist[n,0] * 3.262, step[0] * 2057000000.0), # parsec to c
              y=-250, is_3d=False, camera=CAM2D)
      label.set_shader(flatsh)
      label.set_alpha(1.5)
