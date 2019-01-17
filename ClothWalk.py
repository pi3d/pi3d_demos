#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import math, random

import demo
import pi3d

import numpy as np

########################################################################
# cloth generation section
########################################################################
class Cloth(object):
  def _gcd(self, a, b):
    """Return greatest common divisor using Euclid's Algorithm."""
    while b:
      a, b = b, a % b
    return a

  def _lcm(self, a, b):
    """Return lowest common multiple."""
    return a * b // self._gcd(a, b)

  def __init__(self, epm=3200, ppm=3200, yarn_colours=[[0, 0, 0], [255, 255, 255]],
                warp_plan=[0], weft_plan=[1], draft_plan=[0, 1], peg_plan=[[1, 0], [1, 0]]):
    self.epm = epm # ends per gpu unit (aka warp threads)
    self.ppm = epm # picks per gpu unit (aka weft threads)
    self.yarn_colours = np.array(yarn_colours)
    # yarn plan numbers refer to yarn_colours index (starting at 0 obviously)
    self.warp_plan = np.array(warp_plan)
    self.weft_plan = np.array(weft_plan)
    # draft aka heald, heddle, shaft, frame: the set of wires attached to a liftable frame
    # position in the array corresponds to warp thread number is the 'column' of the peg_plan
    self.draft_plan = np.array(draft_plan)
    # peg or lifting plan, rows are weft insertions, column are shafts, 0 is down 1 is up
    self.peg_plan = np.array(peg_plan)
    self.tex = None
    self.recalc()

  def recalc(self):
    pick_rpt = self.peg_plan.shape[0] # length in 1st dimension of array
    draft_rpt = self.draft_plan.size # length of array
    weft_rpt = self.weft_plan.size
    warp_rpt = self.warp_plan.size

    # find the size of the sample
    self.wv_width = self._lcm(warp_rpt, draft_rpt) # lowest common multiple of weave and yarn patterns
    self.wv_height = self._lcm(weft_rpt, pick_rpt)

    # extend each of the plans to the size of the sample
    self.warp_plan = np.tile(self.warp_plan, (self.wv_width // warp_rpt))
    self.weft_plan = self.weft_plan.reshape((weft_rpt, 1)) # make into vertical array
    self.weft_plan = np.tile(self.weft_plan, (self.wv_height // weft_rpt, 1))
    self.draft_plan = np.tile(self.draft_plan, (self.wv_width // draft_rpt))
    self.peg_plan = np.tile(self.peg_plan, (self.wv_height // pick_rpt, 1))

    lifts = self.peg_plan[:, self.draft_plan] # generate an up/down map for the plan
    # then fill it with the yarn for warp if it's up or weft if it's down
    self.yarn_plan = lifts * self.warp_plan + (lifts * -1 + 1) * self.weft_plan
    wv = self.yarn_colours[self.yarn_plan].astype(np.uint8) # wv takes the [R,G,B] from yarn colours
    self.img = wv # ndarray in case needed elsewhere
    if self.tex is None:
      self.tex = pi3d.Texture(wv)
    else:
      self.tex.update_ndarray(self.img)
    ########################################################################


cloth = Cloth(
  yarn_colours = [ # RGB values 0-255
    [50, 10, 20],  #0 = brown
    [40, 55, 20],  #1 = kaki
    [120, 150, 40],#2 = dull yellow
    [80, 200, 120],#3 = teal
    [30, 5, 110],  #4 = royal blue
    [100, 10, 140],#5 = purple
    [255, 20, 220] #6 = violet
  ],
  warp_plan = ([3] * 8 + [3, 0, 2] * 2 + [4, 4]) * 3 + [0] * 7 + [5],
  weft_plan = ([2] * 8 + [1, 5, 4] * 2 + [6, 5]) * 3 + [0, 1] * 3 + [0, 5],
  draft_plan = [0,1,2,3, 0,1,2,3, 1,0,3,2, 1,0,3,2], # simple herringbone
  peg_plan = [
    [0,1,1,0],
    [1,1,0,0],
    [1,0,0,1],
    [0,0,1,1]
  ])

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100, frames_per_second=30)
DISPLAY.set_background(0.4, 0.8, 0.8, 1.0)      # r,g,b,alpha
# yellowish directional light blueish ambient light
pi3d.Light(lightpos=(1, -1, -3), lightcol =(1.0, 1.0, 0.8), lightamb=(0.45, 0.5, 0.6))

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
mymap.set_draw_details(shader, [cloth.tex, bumpimg, reflimg], 128.0 * cloth.wv_width / 8.0, 0.0)
mymap.set_fog(*FOG)

#Create monument
monument = pi3d.Model(file_string="models/pi3d.obj", name="monument")
monument.set_shader(shinesh)
monument.set_draw_details(shinesh, [cloth.tex, bumpimg, reflimg], ntiles=cloth.ppm/8,
                          shiny=0.03, umult=cloth.epm/cloth.wv_width, vmult=cloth.ppm/cloth.wv_height)
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
    elif k==ord('y'): # yellowify
      cloth.yarn_colours[3] = [255, 255, 0]
      cloth.recalc()
    elif k==ord('u'): # alter weft plan
      cloth.weft_plan = np.array(([3] * 15 + [2] * 10) * 2 + [0] * 7)
      cloth.recalc()
    elif k==ord('i'): # alter warp plan
      cloth.warp_plan = np.array(([0] * 13 + [4] * 13) * 2 + [0] * 4)
      cloth.recalc()
    elif k==ord('o'): # alter peg plan to hopsack
      cloth.peg_plan = np.array([[0,0,1,1],[0,0,1,1],[1,1,0,0],[1,1,0,0]])
      cloth.recalc()
    elif k==ord('p'): # alter draft plan to non-herringbone
      cloth.draft_plan = np.array([3,2,1,0] * 4)
      cloth.recalc()
    elif k==27:  #Escape key
      mykeys.close()
      mymouse.stop()
      DISPLAY.stop()
      break
