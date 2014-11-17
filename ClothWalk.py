#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import math, random

import demo
import pi3d

import numpy as np
from PIL import Image

########################################################################
# cloth generation section
########################################################################
def gcd(a, b):
    """Return greatest common divisor using Euclid's Algorithm."""
    while b:      
        a, b = b, a % b
    return a

def lcm(a, b):
    """Return lowest common multiple."""
    return a * b // gcd(a, b)

def lcmm(*args):
    """Return lcm of args."""   
    return reduce(lcm, args)

PPM = 1800 # picks per m (aka weft threads)
EPM = 1800 # ends per m (aka warp threads)
yarn_colours = np.array([ # RGB values 0-255
[50, 10, 20],
[40, 55, 20],
[120, 150, 40],
[80, 200, 120],
[30, 5, 110],
[100, 10, 140],
[255, 20, 220]])
# yarn plan numbers refer to yarn_colours index (starting at 0 obviously)
warp_plan = np.array(([3]*8 + [3,0,2]*2 + [4,4])*3 + [0]*7 + [5])
weft_plan = np.array(([2]*8 + [1,5,4]*2 + [6,5])*3 + [0,1]*3 + [0,5])
# heald, heddle, shaft, frame: the set of wires attached to a liftable frame
# position in the array corresponds to warp thread number is the 'column' of the peg_plan
heald_plan = np.array([0,1,2,3, 0,1,2,3, 1,0,3,2, 1,0,3,2]) # simple herringbone
# rows are weft insertions, column are shafts, 0 is down 1 is up
peg_plan = np.array([
[0,1,1,0],
[1,1,0,0],
[1,0,0,1],
[0,0,1,1]])

pick_rpt = peg_plan.shape[0]
heald_rpt = heald_plan.size
weft_rpt = weft_plan.size
warp_rpt = warp_plan.size
wv_width = lcm(warp_rpt, heald_rpt) # lowest common multiple
wv_height = lcm(weft_rpt, pick_rpt)

warp_plan = np.tile(warp_plan, (wv_width // warp_rpt))
weft_plan = weft_plan.reshape((weft_rpt, 1)) # make into vertical array
weft_plan = np.tile(weft_plan, (wv_height // weft_rpt, 1))
heald_plan = np.tile(heald_plan, (wv_width // heald_rpt))
peg_plan = np.tile(peg_plan, (wv_height // pick_rpt, 1))

lifts = peg_plan[:,heald_plan[:]] # generate an up/down map for the plan
# then fill it with the yarn for warp if it's up or weft if it's down
yarn_plan = lifts[:,:] * warp_plan[:] + (lifts * -1 + 1)[:,:] * weft_plan[:]
wv = yarn_colours[yarn_plan[:,:]].astype(np.uint8) # wv takes the [R,G,B] from yarn colours

im = Image.fromarray(wv, 'RGB')
clothimg = pi3d.Texture(im)
########################################################################

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100)
DISPLAY.set_background(0.4, 0.8, 0.8, 1.0)      # r,g,b,alpha
# yellowish directional light blueish ambient light
pi3d.Light(lightpos=(1, -1, -3), lightcol =(1.0, 1.0, 0.8), lightamb=(0.25, 0.2, 0.3))

#========================================

# load shader
shader = pi3d.Shader("uv_bump")
shinesh = pi3d.Shader("uv_reflect")
flatsh = pi3d.Shader("uv_flat")

bumpimg = pi3d.Texture("textures/weave.png")
reflimg = pi3d.Texture("textures/stars.jpg")
rockimg = pi3d.Texture("textures/rock1.jpg")

FOG = ((0.3, 0.3, 0.4, 0.8), 650.0)
TFOG = ((0.2, 0.24, 0.22, 1.0), 150.0)

#myecube = pi3d.EnvironmentCube(900.0,"HALFCROSS")
ectex=pi3d.loadECfiles("textures/ecubes","skybox_hall")
myecube = pi3d.EnvironmentCube(size=900.0, maptype="FACES", name="cube")
myecube.set_draw_details(flatsh, ectex)


# Create elevation map
mapwidth = 1000.0
mapdepth = 1000.0
mapheight = 60.0
mountimg1 = pi3d.Texture("textures/mountains3_512.jpg")
mymap = pi3d.ElevationMap("textures/mountainsHgt.jpg", name="map",
                     width=mapwidth, depth=mapdepth, height=mapheight,
                     ntiles=128, divx=32, divy=32) #testislands.jpg
mymap.set_draw_details(shader, [clothimg, bumpimg, reflimg], 128.0, 0.0)
mymap.set_fog(*FOG)

#Create monument
monument = pi3d.Model(file_string="models/pi3d.obj", name="monument")
monument.set_shader(shinesh)
monument.set_draw_details(shinesh, [clothimg, bumpimg, reflimg], ntiles=PPM/8,
                          shiny=0.03, umult=EPM/wv_width, vmult=PPM/wv_height)
monument.set_fog(*FOG)
monument.translate(100.0, -mymap.calcHeight(100.0, 235) + 12.0, 235.0)
monument.scale(20.0, 20.0, 20.0)
monument.rotateToY(-25)

#screenshot number
scshots = 1

#avatar camera
rot = 0.0
tilt = 0.0
avhgt = 3.5
xm = 100.0
zm = 220.0
ym = mymap.calcHeight(xm, zm) + avhgt

# Fetch key presses
mykeys = pi3d.Keyboard()
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()

omx, omy = mymouse.position()

CAMERA = pi3d.Camera.instance()

# Display scene and rotate cuboid
while DISPLAY.loop_running():
  CAMERA.reset()
  CAMERA.rotate(tilt, rot, 0)
  CAMERA.position((xm, ym, zm))

  # for opaque objects it is more efficient to draw from near to far as the
  # shader will not calculate pixels already concealed by something nearer
  monument.draw()
  mymap.draw()
  myecube.draw()

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
