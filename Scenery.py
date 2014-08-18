#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" As per ForestWalk but showing use of the String.quick_change() method
for rapidly changing text
"""

import math,random

import demo
import pi3d
import pickle
import time

print('''W key for each oar stroke. You must row between 20 and 30 strokes
per minute to go in a straight line. Faster than that and you will turn
left, slower and you will turn right

A and D also turn and ' and / move the camera up and down
delete scenery/map00.pkl to re-generate the pickle files
Esc to quit
''')

from pi3d.util.Scenery import Scene, SceneryItem

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create()
DISPLAY.set_background(0.5, 0.4, 0.6,1.0)      # r,g,b,alpha
# yellowish directional light blueish ambient light
pi3d.Light(lightpos=(1, -1, -3), lightcol =(0.7, 0.7, 0.6), lightamb=(0.4, 0.3, 0.5))

MSIZE = 1000
NX = 5
NZ = 5
sc = Scene('scenery', MSIZE, NX, NZ)
    
# load shaders
shader = pi3d.Shader("uv_bump")
shinesh = pi3d.Shader("uv_reflect")
flatsh = pi3d.Shader("uv_flat")
matsh = pi3d.Shader("mat_reflect")

FOG = ((0.3, 0.3, 0.41, 0.95), 500.0)
TFOG = ((0.3, 0.3, 0.4, 0.95), 300.0)

for i in range(5):
  for j in range(5):
    sc.scenery_list['fjord_elev{}{}'.format(i, j)] = SceneryItem(
          (0.5 + i) * MSIZE, 0.0, (0.5 + j) * MSIZE, ['fjord_tex{}{}'.format(i, j), 
          'n_norm000'], shader, 128, height=300.0, threshold=1500.0)
    sc.scenery_list['map{}{}'.format(i, j)] = SceneryItem(
          (0.5 + i) * MSIZE, 40.0, (0.5 + j) * MSIZE, ['n_norm000', 'stars3'], 
          matsh, 32.0, 0.6, height=10.0, alpha=0.8, priority=2, threshold=950.0)
          
    sc.scenery_list['tree01'] = SceneryItem(1680, 0, 4300, ['tree2'], shader, texture_flip=True, priority=10, 
                              put_on='fjord_elev14', threshold = 650.0,
                              model_details={'model':'tree', 'w':150, 'd':100, 'n':15, 'maxs':6.0, 'mins':1.0})
    sc.scenery_list['tree02'] = SceneryItem(1750, 0, 4300, ['tree1'], shader, texture_flip=True, priority=5, 
                              put_on='fjord_elev14', threshold = 650.0,
                              model_details={'model':'tree', 'w':200, 'd':100, 'n':10, 'maxs':5.0, 'mins':3.0})
    sc.scenery_list['tree03'] = SceneryItem(3400, 0, 4150, ['hornbeam2'], shader, texture_flip=True, priority=4, 
                              put_on='fjord_elev34', threshold = 650.0,
                              model_details={'model':'tree', 'w':100, 'd':50, 'n':20, 'maxs':6.0, 'mins':2.0})

try:
  f = open('scenery/map00.pkl', 'r') #do this once to create the pickled objects
  f.close()
except IOError:
  sc.do_pickle(FOG)

#myecube = pi3d.EnvironmentCube(900.0,"HALFCROSS")
ectex = pi3d.loadECfiles("textures/ecubes","sbox")
myecube = pi3d.EnvironmentCube(size=7000.0, maptype="FACES", name="cube")
myecube.set_draw_details(flatsh, ectex)
myecube.set_fog((0.3, 0.3, 0.4, 1.0), 5000)

#time checking
chktm = 1.0
lastchk = time.time()
cleartm = 10.0
lastclear = lastchk
laststroke = lastchk
#physics
MASS = 500.0
DRAGF = 30.0
MAXF = 12.0
MINV = 0.05
MAXR = 1.0
RACC = 0.05
DECAY = 0.95
TLEFT = 2.0
TRIGHT = 3.0
vel = MINV
acc = 0.0
force = MAXF
rvel = 0.0

rot = 0.0
tilt = 4.0
avhgt = 3.5
xm = 1447.0
zm = 4337.0
ym = 50.0
fmap = None
cmap = None
# Fetch key presses
mykeys = pi3d.Keyboard()
#mymouse = pi3d.Mouse(restrict = False)
#mymouse.start()

#omx, omy = mymouse.position()

CAMERA = pi3d.Camera(lens=(1.0, 10000.0, 55.0, 1.6))
####################
#this block added for fast text changing
CAMERA2D = pi3d.Camera(is_3d=False)
myfont = pi3d.Font('fonts/FreeMonoBoldOblique.ttf', codepoints='0123456789. -xzFPS:')
myfont.blend = True
tstring = "x{:.2f} z{:.2f} FPS:{:.1f} ".format(xm, zm, 60.2)
lasttm = 0.0
tdel = 0.23
fcount = 0
mystring = pi3d.String(camera=CAMERA2D, font=myfont, is_3d=False, string=tstring)
mystring.set_shader(flatsh)
(lt, bm, ft, rt, tp, bk) = mystring.get_bounds()
xpos = (-DISPLAY.width + rt - lt) / 2.0
ypos = (-DISPLAY.height + tp - bm) / 2.0
mystring.position(xpos, ypos, 1.0)
mystring.draw()
####################

# Display scene and move camera
while DISPLAY.loop_running():
  ####################
  #this block added for fast text changing
  tm = time.time()
  fcount += 1
  #if tm > (lasttm + tdel):
  #  newtstring = "x{:.2f} z{:.2f} FPS:{:.1f} ".format(xm, zm, fcount / (tm - lasttm))
  #  mystring.quick_change(newtstring)
  #  lasttm = tm
  #  fcount = 0
  #mystring.draw()
  #################### scenery loading
  if tm > (lastchk + chktm):
    xm, zm, cmap = sc.check_scenery(xm, zm)
    fmap = sc.scenery_list['fjord_elev{}{}'.format(int(xm/MSIZE), int(zm/MSIZE))].shape
    lastchk = tm
  #################### clear out unused scenery
  if tm > (lastclear + cleartm):
    sc.clear_scenery(lastclear - 2.0 * cleartm)
    lastclear = tm
  ####################
  CAMERA.reset()
  CAMERA.rotate(tilt, rot, 0)
  CAMERA.position((xm, ym, zm))
  myecube.position(xm, ym, zm)

  myecube.draw()
  for s in sc.draw_list:
    s.shape.draw()
    s.last_drawn = tm
  
  #mx, my = mymouse.position()

  #rot -= (mx-omx)*0.2
  #tilt += (my-omy)*0.2
  #omx=mx
  #omy=my

  force *= DECAY
  rot += rvel
  acc = (force - vel * vel * DRAGF) / MASS
  vel += acc * 0.05
  if vel < MINV:
    vel = MINV
  #print('f{:.2f} a{:.2f} v{:.2f}'.format(force, acc, vel))
  dx = -math.sin(math.radians(rot)) * vel
  dz = math.cos(math.radians(rot)) * vel
  xm += dx
  zm += dz
  if fmap and fmap.calcHeight(xm, zm) < 35.0:
    if cmap:
      ym = cmap.calcHeight(xm, zm) + avhgt
  else:
    xm -=dx
    zm -=dz

  if (tm - laststroke) > TRIGHT:
    rvel -= RACC
    if rvel > 0:
      rvel = 0
    elif rvel < -MAXR:
      rvel = -MAXR
    laststroke = tm
  #Press ESCAPE to terminate
  k = mykeys.read()
  if k >-1:
    if k==ord('w'):  #key W
      if (tm - laststroke) > TRIGHT:
        rvel -= RACC
        if rvel < -MAXR:
          rvel = -MAXR
      elif (tm - laststroke) < TLEFT:
        rvel += RACC
        if rvel < 0:
          rvel = 0
        elif rvel > MAXR:
          rvel = MAXR
      else:
        rvel = 0
      force = MAXF
      laststroke = tm
    elif k==ord('s'):  #kry S
      xm += math.sin(math.radians(rot)) * 2.0
      zm -= math.cos(math.radians(rot)) * 2.0
      if cmap:
        ym = cmap.calcHeight(xm, zm) + avhgt
    elif k==ord("'"):   #key '
      tilt -= 2.0
    elif k==ord('/'):   #key /
      tilt += 2.0
    elif k==ord('a'):   #key A
      rot -= 2
    elif k==ord('d'):  #key D
      rot += 2
    elif k==27:  #Escape key
      mykeys.close()
      #mymouse.stop()
      DISPLAY.stop()
      break
