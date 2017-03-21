#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Based on ForestWalk but using four different textures for the
EnvironmentMap. Functionality added in v2.19
"""

import math,random

import demo
import pi3d

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=200, y=200)
DISPLAY.set_background(0.4,0.8,0.8,1)      # r,g,b,alpha
# yellowish directional light blueish ambient light
pi3d.Light(lightpos=(1, -1, -3), lightcol=(1.0, 1.0, 0.8), lightamb=(0.25, 0.2, 0.3))

#========================================

# load shader
shader = pi3d.Shader("uv_env_map")
flatsh = pi3d.Shader("uv_flat")

# tree textures
tree2img = pi3d.Texture("textures/tree2.png")
tree1img = pi3d.Texture("textures/tree1.png")
# ground textures
pongimg = pi3d.Texture("textures/stripwood.jpg")
mountimg1 = pi3d.Texture("textures/mountains3_512.jpg")
reflimg = pi3d.Texture("textures/stars.jpg")
strawimg = pi3d.Texture("textures/straw1.jpg")
# ground normal maps
mudimg = pi3d.Texture("textures/mudnormal.jpg")
bumpimg = pi3d.Texture("textures/grasstile_n.jpg")
rockimg = pi3d.Texture("textures/rocktile2.jpg")
floorimg = pi3d.Texture("textures/floor_nm.jpg")

FOG = ((0.3, 0.3, 0.4, 0.8), 650.0)
TFOG = ((0.2, 0.24, 0.22, 1.0), 150.0)

#myecube = pi3d.EnvironmentCube(900.0,"HALFCROSS")
ectex=pi3d.loadECfiles("textures/ecubes","sbox")
myecube = pi3d.EnvironmentCube(size=900.0, maptype="FACES", name="cube")
myecube.set_draw_details(flatsh, ectex)

# Create elevation map
mapsize = 1000.0
mapheight = 120.0
mymap = pi3d.ElevationMap("textures/mountainsHgt.png", name="map",
                     width=mapsize, depth=mapsize, height=mapheight,
                     divx=32, divy=32, texmap="textures/mars_height.png") 
''' texmap represents four different diffuse textures and four normal maps
allocated according to the lowest to highest luminance values on the map'''
mymap.set_draw_details(shader, [pongimg, mudimg,
                                mountimg1, bumpimg, 
                                reflimg, floorimg,
                                strawimg, rockimg], 8.0, 0.0, umult=16.0, vmult=16.0)
mymap.set_fog(*FOG)

#Create tree models
treeplane = pi3d.Plane(w=4.0, h=5.0)

treemodel1 = pi3d.MergeShape(name="baretree")
treemodel1.add(treeplane.buf[0], 0,0,0)
treemodel1.add(treeplane.buf[0], 0,0,0, 0,90,0)

treemodel2 = pi3d.MergeShape(name="bushytree")
treemodel2.add(treeplane.buf[0], 0,0,0)
treemodel2.add(treeplane.buf[0], 0,0,0, 0,60,0)
treemodel2.add(treeplane.buf[0], 0,0,0, 0,120,0)

#Scatter them on map using Merge shape's cluster function
mytrees1 = pi3d.MergeShape(name="trees1")
mytrees1.cluster(treemodel1.buf[0], mymap,0.0,0.0,200.0,200.0,10,"",8.0,3.0)
mytrees1.set_draw_details(flatsh, [tree2img], 0.0, 0.0)
mytrees1.set_fog(*TFOG)

mytrees2 = pi3d.MergeShape(name="trees2")
mytrees2.cluster(treemodel2.buf[0], mymap,0.0,0.0,200.0,200.0,15,"",6.0,3.0)
mytrees2.set_draw_details(flatsh, [tree1img], 0.0, 0.0)
mytrees2.set_fog(*TFOG)

#screenshot number
scshots = 1

#avatar camera
rot = 0.0
tilt = 0.0
avhgt = 3.5
xm = 0.0
zm = 0.0
ym = mymap.calcHeight(xm, zm) + avhgt
step = [0.0, 0.0, 0.0]
norm = None
crab = False

# Fetch key presses
mykeys = pi3d.Keyboard()
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()

CAMERA = pi3d.Camera(absolute=False)
roll = 0.0
# Display scene and rotate cuboid
while DISPLAY.loop_running():
  xm, ym, zm = CAMERA.relocate(rot, tilt, point=[xm, ym, zm], distance=step, 
                              normal=norm, crab=crab, slope_factor=0.5)
  if step != [0.0, 0.0, 0.0]: #i.e. previous loop set movmement
    ym, norm = mymap.calcHeight(xm, zm, True)
    ym += avhgt
    step = [0.0, 0.0, 0.0]
  myecube.position(xm, ym, zm)
  CAMERA.rotateZ(roll)
  roll = 0.0

  mymap.draw()
  if abs(xm) > 300:
    mymap.position(math.copysign(1000,xm), 0.0, 0.0)
    mymap.draw()
  if abs(zm) > 300:
    mymap.position(0.0, 0.0, math.copysign(1000,zm))
    mymap.draw()
    if abs(xm) > 300:
      mymap.position(math.copysign(1000,xm), 0.0, math.copysign(1000,zm))
      mymap.draw()
  mymap.position(0.0, 0.0, 0.0)
  myecube.draw()
  mytrees1.draw()
  mytrees2.draw()

  mx, my = mymouse.velocity() #change to position() if Camera switched to absolute=True (default)
  buttons = mymouse.button_status()

  rot = - mx * 0.2
  tilt = my * 0.2

  #Press ESCAPE to terminate
  k = mykeys.read()
  if k >-1 or buttons > mymouse.BUTTON_UP:
    if k == 119 or buttons == mymouse.LEFT_BUTTON:  #key w forward
      step = [0.5, 0.0, 0.5]
      crab = False
    elif k == 115 or buttons == mymouse.RIGHT_BUTTON:  #kry s back
      step = [-0.25, 0.0, -0.25]
      crab = False
    elif k == 97:   #key a crab left
      step = [0.25, 0.0, 0.25]
      crab = True
    elif k == 100:  #key d crab right
      step = [-0.25, 0.0, -0.25]
      crab = True
    elif k == 112:  #key p picture
      pi3d.screenshot("forestWalk" + str(scshots) + ".jpg")
      scshots += 1
    elif k == 10:   #key RETURN
      mc = 0
    elif k == 27:  #Escape key
      mykeys.close()
      mymouse.stop()
      DISPLAY.stop()
      break
    elif k == ord('f'):
      roll = 1.0


    halfsize = mapsize / 2.0
    xm = (xm + halfsize) % mapsize - halfsize # wrap location to stay on map -500 to +500
    zm = (zm + halfsize) % mapsize - halfsize
