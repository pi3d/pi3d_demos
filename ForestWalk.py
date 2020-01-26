#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" First person view using ElevationMap.calcHeight function to move over
undulating surface, MergeShape.cluster to create a forest that renders quickly,
uv_reflect shader is used give texture and reflection to a monument, fog is
applied to objects so that their details become masked with distance.
The lighting is also defined with a yellow directional tinge and an indigo tinge
to the ambient light.

The ElevationMap is designed to "tile" as the Camera moves towards an edge.
Notice that the height image mountainsHgt.png is not jpeg which would cause
compression inaccuracies and has an extra row of pixels duplicating the
opposite edge (33x33) so that there are no "cracks"

In this version the Camera positioning is done using the relocate() method
which can be used to take into account steepness of the slope by altering
the slope_factor argument. NB the Camera movements are relative, by setting
the argument absolute=False
"""

import math,random, time

import demo
import pi3d

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100, frames_per_second=30)
DISPLAY.set_background(0.4,0.8,0.8,1)      # r,g,b,alpha
# yellowish directional light blueish ambient light
pi3d.Light(lightpos=(1, -1, -3), lightcol=(1.0, 1.0, 0.8), lightamb=(0.25, 0.2, 0.3))

#========================================

# load shader
shader = pi3d.Shader("uv_bump")
shinesh = pi3d.Shader("mat_reflect")
flatsh = pi3d.Shader("uv_flat")

tree2img = pi3d.Texture("textures/tree2.png", mipmap=False)
tree1img = pi3d.Texture("textures/tree1.png", mipmap=False)
hb2img = pi3d.Texture("textures/hornbeam2.png", mipmap=False)
bumpimg = pi3d.Texture("textures/grasstile_n.jpg")
reflimg = pi3d.Texture("textures/stars.jpg")
floorimg = pi3d.Texture("textures/floor_nm.jpg")

FOG = ((0.3, 0.3, 0.4, 0.8), 650.0)
TFOG = ((0.2, 0.24, 0.22, 1.0), 150.0)

#myecube = pi3d.EnvironmentCube(900.0,"HALFCROSS")
ectex=pi3d.loadECfiles("textures/ecubes","sbox")
myecube = pi3d.EnvironmentCube(size=900.0, maptype="FACES", name="cube")
myecube.set_draw_details(flatsh, ectex)

# Create elevation map
mapsize = 1000.0
mapheight = 60.0
mountimg1 = pi3d.Texture("textures/mountains3_512.jpg")
mymap = pi3d.ElevationMap("textures/mountainsHgt.png", name="map",
                     width=mapsize, depth=mapsize, height=mapheight,
                     divx=32, divy=32) 
mymap.set_draw_details(shader, [mountimg1, bumpimg, reflimg], 128.0, 0.0)
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
mytrees1.cluster(treemodel1.buf[0], mymap,0.0,0.0,200.0,200.0,20,"",8.0,3.0)
mytrees1.set_draw_details(flatsh, [tree2img], 0.0, 0.0)
mytrees1.set_fog(*TFOG)

mytrees2 = pi3d.MergeShape(name="trees2")
mytrees2.cluster(treemodel2.buf[0], mymap,0.0,0.0,200.0,200.0,20,"",6.0,3.0)
mytrees2.set_draw_details(flatsh, [tree1img], 0.0, 0.0)
mytrees2.set_fog(*TFOG)

mytrees3 = pi3d.MergeShape(name="trees3")
mytrees3.cluster(treemodel2, mymap,0.0,0.0,300.0,300.0,20,"",4.0,2.0)
mytrees3.set_draw_details(flatsh, [hb2img], 0.0, 0.0)
mytrees3.set_fog(*TFOG)

#Create monument
monument = pi3d.Model(file_string="models/pi3d.obj", name="monument")
monument.set_shader(shinesh)
monument.set_normal_shine(bumpimg, 16.0, reflimg, 0.1, bump_factor=0.05)
monument.set_fog(*FOG)
monument.translate(100.0, -mymap.calcHeight(100.0, 235) + 12.0, 235.0)
monument.scale(10.0, 10.0, 10.0)
monument.rotateToY(-115)

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
mymouse = pi3d.Mouse(restrict=False)
mymouse.start()

CAMERA = pi3d.Camera(absolute=False) # you can change this to True but below use: mx, my = mymouse.position()
roll = 0.0
# Display scene and rotate cuboid
n = 0
start = time.time()
while DISPLAY.loop_running():
  xm, ym, zm = CAMERA.relocate(rot, tilt, point=[xm, ym, zm], distance=step, 
                              normal=norm, crab=crab, slope_factor=1.5)
  if step != [0.0, 0.0, 0.0]: #i.e. previous loop set movmement
    ym, norm = mymap.calcHeight(xm, zm, True)
    ym += avhgt
    step = [0.0, 0.0, 0.0]
  myecube.position(xm, ym, zm)
  CAMERA.rotateZ(roll)
  roll = 0.0

  # For opaque objects it is more efficient to draw from near to far as the
  # shader will not calculate pixels already concealed by something nearer.
  # In this case the partially transparent trees have to be drawn after
  # things behind them.
  monument.draw()
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
  mytrees3.draw()

  mx, my = mymouse.velocity() #change to position() if Camera switched to absolute=True (default)
  buttons = -1 #mymouse.button_status()

  rot = - mx * 0.2
  tilt = my * 0.2

  n += 1
  #Press ESCAPE to terminate
  k = mykeys.read()
  #print(len(DISPLAY.keys_pressed))
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
print("{:.1f}fps".format(n / (time.time() - start)))