#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" As per ForestWalk but showing use of the String.quick_change() method
for rapidly changing text
"""

import math,random

import demo
import pi3d

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100, frames_per_second=30)
DISPLAY.set_background(0.4,0.8,0.8,0)      # r,g,b,alpha
# yellowish directional light blueish ambient light
pi3d.Light(lightpos=(1, -1, -3), lightcol =(1.0, 1.0, 0.8), lightamb=(0.25, 0.2, 0.3))

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
rockimg = pi3d.Texture("textures/rock1.jpg")

FOG = ((0.3, 0.3, 0.4, 0.8), 650.0)
TFOG = ((0.2, 0.24, 0.22, 0.6), 180.0) #NB see line 150+ and problems with draw order of MergeShapes

#myecube = pi3d.EnvironmentCube(900.0,"HALFCROSS")
ectex=pi3d.loadECfiles("textures/ecubes","sbox")
myecube = pi3d.EnvironmentCube(size=900.0, maptype="FACES", name="cube")
myecube.set_draw_details(flatsh, ectex)

# Create elevation map
mapwidth = 1000.0
mapdepth = 1000.0
mapheight = 60.0
mountimg1 = pi3d.Texture("textures/mountains3_512.jpg")
mymap = pi3d.ElevationMap("textures/mountainsHgt.jpg", name="map",
                     width=mapwidth, depth=mapdepth, height=mapheight,
                     divx=32, divy=32) #testislands.jpg
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
monument.set_normal_shine(bumpimg, 16.0, reflimg, 0.4)
monument.set_fog(*FOG)
monument.translate(100.0, -mymap.calcHeight(100.0, 240) + 5.8, 240.0)
monument.scale(10.0, 10.0,10.0)
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

# Fetch key presses
mykeys = pi3d.Keyboard()
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()

omx, omy = mymouse.position()

CAMERA = pi3d.Camera.instance()
####################
#this block added for fast text changing
import time
CAMERA2D = pi3d.Camera(is_3d=False)
myfont = pi3d.Font('fonts/NotoSerif-Regular.ttf', codepoints='0123456789. FPStm:')
myfont.blend = True
tstring = "{:.0f}FPS tm:{:.1f} ".format(60,time.time())
lasttm = time.time()
tdel = 0.23
fcount = 0
mystring = pi3d.String(camera=CAMERA2D, font=myfont, is_3d=False, string=tstring)
mystring.set_shader(flatsh)
(lt, bm, ft, rt, tp, bk) = mystring.get_bounds()
xpos = (-DISPLAY.width + rt - lt) / 2.0
ypos = (-DISPLAY.height + tp - bm) / 2.0
mystring.position(xpos, ypos, 1.0)
mystring.draw() # NB has to be drawn before quick_change() is called as buffer needs to exist
####################

# Display scene and move camera
while DISPLAY.loop_running():
  CAMERA.reset()
  CAMERA.rotate(tilt, rot, 0)
  CAMERA.position((xm, ym, zm))
  myecube.position(xm, ym, zm)

  # for opaque objects it is more efficient to draw from near to far as the
  # shader will not calculate pixels already concealed by something nearer
  monument.draw()
  mymap.draw()
  myecube.draw() # put here to allow alpha fog
  mytrees3.draw()
  mytrees2.draw()
  mytrees1.draw()
#  myecube.draw()
  ####################
  #this block added for fast text changing
  tm = time.time()
  fcount += 1
  if tm > (lasttm + tdel):
    newtstring = "{:.0f}FPS tm:{:.1f}".format(fcount / (tm - lasttm), tm)
    mystring.quick_change(newtstring)
    lasttm = tm
    fcount = 0
  mystring.draw()
  ####################

  mx, my = mymouse.position()

  #if mx>display.left and mx<display.right and my>display.top and my<display.bottom:
  rot -= (mx-omx)*0.2
  tilt += (my-omy)*0.2
  omx=mx
  omy=my

  #Press ESCAPE to terminate
  k = mykeys.read()
  if k >-1:
    if k==119:  #key W
      xm -= math.sin(math.radians(rot))
      zm += math.cos(math.radians(rot))
      ym = mymap.calcHeight(xm, zm) + avhgt
    elif k==115:  #kry S
      xm += math.sin(math.radians(rot))
      zm -= math.cos(math.radians(rot))
      ym = mymap.calcHeight(xm, zm) + avhgt
    elif k==39:   #key '
      tilt -= 2.0
    elif k==47:   #key /
      tilt += 2.0
    elif k==97:   #key A
      rot -= 2
    elif k==100:  #key D
      rot += 2
    elif k==112:  #key P
      pi3d.screenshot("forestWalk"+str(scshots)+".jpg")
      scshots += 1
    elif k==10:   #key RETURN
      mc = 0
    elif k==27:  #Escape key
      mykeys.close()
      mymouse.stop()
      DISPLAY.stop()
      break
