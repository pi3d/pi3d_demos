#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Use MergeShape.billboard() with an array of pi3d.Sprite objects. 
"""

import math, time

import demo
import pi3d

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=0, y=0, background=(0.4, 0.8, 0.8, 1.0))
# load shaders
shader = pi3d.Shader("uv_bump")
flatsh = pi3d.Shader("uv_flat")

hb2img = pi3d.Texture("textures/hornbeam2.png", mipmap=False)
bumpimg = pi3d.Texture("textures/grasstile_n.jpg")

FOG = ((0.3, 0.3, 0.4, 0.8), 350.0)
TFOG = ((0.2, 0.24, 0.22, 0.9), 100.0)

# Create skybox
ectex=pi3d.loadECfiles("textures/ecubes","sbox")
myecube = pi3d.EnvironmentCube(size=900.0, maptype="FACES", name="cube")
myecube.set_draw_details(flatsh, ectex)

# Create elevation map
mapsize = 1000.0
mapheight = 80.0
mountimg1 = pi3d.Texture("textures/mountains3_512.jpg")
mymap = pi3d.ElevationMap("textures/mountainsHgt.png", name="map",
                     width=mapsize, depth=mapsize, height=mapheight,
                     divx=32, divy=32) 
mymap.set_draw_details(shader, [mountimg1, bumpimg], 128.0, 0.0)
mymap.set_fog(*FOG)

# Create billboard trees
tree_sprite = pi3d.Sprite(w=hb2img.ix * 0.01, h=hb2img.iy * 0.01) # this isn't a square image
trees = pi3d.MergeShape()
trees.cluster(tree_sprite, mymap, 0.0, 0.0, 300.0, 600.0, 1000, "", 4.0, 2.0, billboard=True)
trees.cluster(tree_sprite, mymap, 150.0, 300.0, 400.0, 50.0, 25, "", 20.0, 10.0, billboard=True) # some big ones too
trees.set_draw_details(shader, [hb2img, bumpimg], 0.0, 0.0)
trees.set_fog(*TFOG)

#avatar camera
rot = 0.0
tilt = 0.0
avhgt = 3.5
xm = 0.0
zm = 0.0
ym = mymap.calcHeight(xm, zm) + avhgt
step = [0.0, 0.1, 0.0] # small no zero y to run trees.billboard prior to starting moving.
norm = None
crab = False

# Fetch key presses
mykeys = pi3d.Keyboard()
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()

CAMERA = pi3d.Camera()

scshots = 0
frame = 0
tm = time.time()
while DISPLAY.loop_running():
  frame += 1
  xm, ym, zm = CAMERA.relocate(rot, tilt, point=[xm, ym, zm], distance=step, 
                              normal=norm, crab=crab, slope_factor=1.5)
  if step != [0.0, 0.0, 0.0]: #i.e. previous loop set movmement
    trees.billboard([xm, ym, zm]) # only do this if moving, not needed when just rotating camera
    ym, norm = mymap.calcHeight(xm, zm, True)
    ym += avhgt
    step = [0.0, 0.0, 0.0]
  myecube.position(xm, ym, zm)

  mymap.draw()
  if abs(xm) > 300:
    mymap.position(math.copysign(1000, xm), 0.0, 0.0)
    mymap.draw()
  if abs(zm) > 300:
    mymap.position(0.0, 0.0, math.copysign(1000, zm))
    mymap.draw()
    if abs(xm) > 300:
      mymap.position(math.copysign(1000,xm), 0.0, math.copysign(1000, zm))
      mymap.draw()
  mymap.position(0.0, 0.0, 0.0)
  myecube.draw()
  trees.draw()

  mx, my = mymouse.position()
  buttons = mymouse.button_status()

  rot = - mx * 0.2
  tilt = my * 0.2

  #Press ESCAPE to terminate
  k = mykeys.read()
  if k >-1 or buttons > mymouse.BUTTON_UP:
    if k == ord('w') or buttons == mymouse.LEFT_BUTTON:  #key w forward
      step = [0.5, 0.0, 0.5]
      crab = False
    elif k == ord('s') or buttons == mymouse.RIGHT_BUTTON:  #key s back
      step = [-0.25, 0.0, -0.25]
      crab = False
    elif k == ord('a'):   #key a crab left
      step = [0.25, 0.0, 0.25]
      crab = True
    elif k == ord('d'):  #key d crab right
      step = [-0.25, 0.0, -0.25]
      crab = True
    elif k == ord('p'):  #key p picture
      pi3d.screenshot("billboard{:04d}.jpg".format(scshots))
      scshots += 1
    elif k == 27:  #Escape key
      mykeys.close()
      mymouse.stop()
      DISPLAY.stop()
      break

    halfsize = mapsize / 2.0
    xm = (xm + halfsize) % mapsize - halfsize # wrap location to stay on map -500 to +500
    zm = (zm + halfsize) % mapsize - halfsize

print("ran at {:5.2f}FPS".format(frame / (time.time() - tm)))
