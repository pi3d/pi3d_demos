#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Music and animation with changing images. Needs some mp3 files in the
music subdirectory and mpg321 installed. You may need to do some tweaking
with the alsa configuration. On jessie I had to edit a line in 
/usr/share/alsa/alsa.conf and sudo amixer cset numid=3 1
to get sound from the 3.5mm jack plug. Google "raspberry pi getting audio working"
"""
import math, random, time, glob, threading
from subprocess import Popen, PIPE, STDOUT

import demo
import pi3d

def _tex_load(tex_list, slot, fName):
  tex_list[slot] = pi3d.Texture(fName, m_repeat=True) # tiling uses alternate mirroring to avoid seams
  
# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=50, y=50, frames_per_second=40)
DISPLAY.set_background(0.4, 0.6, 0.8, 1.0)      # r,g,b,alpha

#persp_cam = pi3d.Camera.instance() # default instance camera perspecive view

#setup textures, light position and initial model position
pi3d.Light((0, 5, 0))
#create shaders
shader = pi3d.Shader("star")
flatsh = pi3d.Shader("uv_flat")
post = pi3d.PostProcess("shaders/filter_outline")

#Create textures
tFiles = glob.glob("textures/*.*")
nTex = len(tFiles)
slot = 0
tex_list = [pi3d.Texture(tFiles[slot]), None] #ensure first texture there
slot = 1
#next texture load in background
t = threading.Thread(target=_tex_load, args=(tex_list, slot % 2, tFiles[slot % nTex]))
t.daemon = True
t.start()

#Create shape
myshape = pi3d.MergeShape()
asphere = pi3d.Sphere(sides=32, slices=32)
myshape.radialCopy(asphere, step=72)
myshape.position(0.0, 0.0, 5.0)
myshape.set_draw_details(shader, [tex_list[0]], 8.0, 0.1)

mysprite = pi3d.Sprite(w=30.0, h=30.0) # size big enought to overflow screen...
mysprite.position(0.0, 0.0, 15.0)
mysprite.set_draw_details(flatsh, [tex_list[0]], umult=4.0, vmult=4.0) # use u/vmult to scale image

# Fetch key presses.
mykeys = pi3d.Keyboard()
pic_next = 5.0
pic_dt = 5.0
tm = 0.0
dt = 0.02
sc = 0.0
ds = 0.001
x = 0.0
dx = 0.001

mFiles = glob.glob("music/*.mp3")
random.shuffle(mFiles)
nMusic = len(mFiles)
iMusic = 0

p = Popen([b"mpg321", b"-R", b"-F", b"testPlayer"], stdout=PIPE, stdin=PIPE)
p.stdin.write(bytearray("LOAD {}\n".format(mFiles[iMusic]), "ascii"))
#p.stdin.write(b"LOAD music/60miles.mp3\n")
p.stdin.flush()
rval, gval, bval = 0.0, 0.0, 0.0
mx, my = 1.0, 1.0
dx, dy = 1.0, 1.0
# Display scene and rotate shape
while DISPLAY.loop_running():
  tm = tm + dt
  sc = (sc + ds) % 10.0
  myshape.set_custom_data(48, [tm, sc, -0.5 * sc])
  
  post.start_capture()
  # 1. drawing objects now renders to an offscreen texture ####################

  mysprite.draw()
  myshape.draw()

  post.end_capture()
  # 2. drawing now back to screen. The texture can now be used by post.draw()

  # 3. redraw these two objects applying a shader effect ###############
  #read several lines so the video frame rate doesn't restrict the music
  flg = True
  while flg:
    st_read = time.time()
    l = p.stdout.readline()
    if (time.time() - st_read) > 0.01:# poss pause in animation waiting for mpg321 info
      flg = False
    if b'@P' in l:
      iMusic = (iMusic + 1) % nMusic
      p.stdin.write(bytearray("LOAD {}\n".format(mFiles[iMusic]), "ascii"))
      p.stdin.flush()
  if b'FFT' in l: #frequency analysis
    val_str = l.split()
    rval = float(val_str[2]) / 115.0
    gval = float(val_str[6]) / 115.0
    bval = float(val_str[10]) / 115.0
  post.draw({48:rval, 49:gval, 50:bval})

  if mx > 3.0:
    dx = -1.0
  elif  mx < 0.0:
    dx = 1.0
  if my > 5.0:
    dy = -1.0
  elif  my < 0.0:
    dy = 1.0
  mx += dx * gval / 100.0
  my += dy * bval / 50.0 
  myshape.scale(mx, my, mx)
  myshape.rotateIncY(0.6471 + rval)
  myshape.rotateIncX(0.513 - bval)
  mysprite.rotateIncZ(0.5)

  if tm > pic_next:
    """change the pictures and start a thread to load into tex_list"""
    pic_next += pic_dt
    myshape.set_draw_details(shader, [tex_list[slot % 2]])
    mysprite.set_draw_details(flatsh, [tex_list[slot % 2]], umult=4.0, vmult=4.0)
    slot += 1
    t = threading.Thread(target=_tex_load, args=(tex_list, slot % 2, tFiles[slot % nTex]))
    t.daemon = True
    t.start()


  k = mykeys.read()
  if k==112:
    pi3d.screenshot("post.jpg")
  elif k==27:
    mykeys.close()
    DISPLAY.destroy()
    break

p.stdin.write(b'QUIT\n')
