#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
"""
This demo shows how numpy arrays can be patched into a Texture using the
Texture.update_ndarray() method. Also Textures can be initialised by passing
an array rather than a string path or PIL.Image

The video frame extraction to numpy array is based on this page from zulco
https://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/

As at Oct 2020 using RPi v4 with OS Buster and fake KMS graphics driver
ffmpeg as included seems to work fine, however the comments below might
apply for other setups. 

Initially I installed ffmpeg using apt-get on the RPi but the results were 
pretty hopeless so I followed the instructions here http://owenashurst.com/?p=242 
exactly i.e. copy paste from his page (but skipped the optional libfaac 
section. And the result was great. However it took several hours to compile
on RPiv.2

NB to keep the pi3d_demos download to a reasonable size I have not uploaded
the video file. You will need to add your own to the same directory as this
python file. You will then need to alter the W and H values to the width
and height in line 34 and the name of the file in line 36. The video will
need to be reasonably small frame size in order for the Raspberry Pi to 
cope with it
"""

import demo
import pi3d
import numpy as np
from PIL import Image, ImageDraw
import subprocess as sp
import threading
import time
import math

W, H, P = 480, 270, 3 # video width, height, bytes per pixel (3 = RGB)

command = [ 'ffmpeg', '-i', 'exercise01.mpg', '-f', 'image2pipe',
                      '-pix_fmt', 'rgb24', '-vcodec', 'rawvideo', '-']
flag = False # use to signal new texture
image = np.zeros((H, W, P), dtype='uint8')

def pipe_thread():
  global flag, image
  pipe = None
  while True:
    st_tm = time.time()
    if pipe is None:
      pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=-1)
    image =  np.frombuffer(pipe.stdout.read(H * W * P), dtype='uint8')
    pipe.stdout.flush() # presumably nothing else has arrived since read()
    pipe.stderr.flush() # ffmpeg sends commentary to stderr
    if len(image) < H * W * P: # end of video, reload
      pipe.terminate()
      pipe = None
    else:
      image.shape = (H, W, P)
      flag = True
    step = time.time() - st_tm
    time.sleep(max(0.04 - step, 0.0)) # adding fps info to ffmpeg doesn't seem to have any effect


t = threading.Thread(target=pipe_thread)
t.daemon = True
t.start()

while flag is False:
  time.sleep(1.0)

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=50, y=50, frames_per_second=25)
DISPLAY.set_background(0.4,0.8,0.8,1)      # r,g,b,alpha
# yellowish directional light blueish ambient light
pi3d.Light(lightpos=(1, -1, -3), lightcol=(1.0, 1.0, 0.8), lightamb=(0.25, 0.2, 0.3))

#========================================

# load shader
shader = pi3d.Shader("uv_bump")
flatsh = pi3d.Shader("uv_flat")

tree2img = pi3d.Texture("textures/tree2.png")
tree1img = pi3d.Texture("textures/tree1.png")
hb2img = pi3d.Texture("textures/hornbeam2.png")
bumpimg = pi3d.Texture("textures/grasstile_n.jpg")
reflimg = pi3d.Texture("textures/stars.jpg")
rockimg = pi3d.Texture("textures/rock1.jpg")

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
tex = pi3d.Texture(image) # can pass numpy array or PIL.Image rather than path as string
monument = pi3d.Sphere(sx=W/100.0, sy=H/20.0, sz=W/20.0)
monument.set_draw_details(shader, [tex, bumpimg], 4.0, umult=2.0)
monument.set_fog(*TFOG)
monument.translate(100.0, -mymap.calcHeight(100.0, 235) + 25.0, 235.0)

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

# Display scene and rotate cuboid
while DISPLAY.loop_running():
  CAMERA.reset()
  CAMERA.rotate(tilt, rot, 0)
  CAMERA.position((xm, ym, zm))
  myecube.position(xm, ym, zm)

  if flag:
    tex.update_ndarray(image, 0) # specify the first GL_TEXTURE0 i.e. first in buf[0].texture
    flag = False
  monument.draw()
  monument.rotateIncY(0.25)
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

  mx, my = mymouse.position()
  buttons = mymouse.button_status()

  rot -= (mx-omx)*0.2
  tilt += (my-omy)*0.2
  omx=mx
  omy=my

  #Press ESCAPE to terminate
  k = mykeys.read()
  if k >-1 or buttons > mymouse.BUTTON_UP:
    dx, dy, dz = CAMERA.get_direction()
    if k == ord("w") or buttons == mymouse.LEFT_BUTTON:  #key W
      xm += dx
      zm += dz
      ym = mymap.calcHeight(xm, zm) + avhgt
    elif k == ord("s") or buttons == mymouse.RIGHT_BUTTON:  #kry S
      xm -= dx
      zm -= dz
      ym = mymap.calcHeight(xm, zm) + avhgt
    elif k == 112:  #key P
      pi3d.screenshot("forestWalk"+str(scshots)+".jpg")
      scshots += 1
    elif k == 27:  #Escape key
      mykeys.close()
      mymouse.stop()
      DISPLAY.stop()
      break

    halfsize = mapsize / 2.0
    xm = (xm + halfsize) % mapsize - halfsize # wrap location to stay on map -500 to +500
    zm = (zm + halfsize) % mapsize - halfsize
