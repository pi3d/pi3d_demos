#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" ForestWalk but with stereoscopic view - i.e. for google cardboard

NB in this example the cameras have been set with a negative separation i.e.
for viewing cross-eyed as most people find this easier without a viewer!!!
If a viewer is used then the line defining CAMERA would need to be changed
to an appropriate +ve separation.

NB also, no camera has been explicitly assigned to the objects so they all
use the default instance and this will be CAMERA.camera_3d so long as the
StereoCam instance was created before any other Camera instance. i.e. it
would be safer really to assign the Camera to each Shape as they are created.

This demo also uses relative rotation for the Camera which is more like
the effect of having a gyro sensor attached to stereo goglles. This can
be efficiently done using the Mouse.velocity() method and the argumente:
Camera(... absolute=False) or just set Camera.absolute = False. Using the
'a' and 'd' keys will rotate the camera about the z axis (roll mode)

Because relative rotations are cumulative with no simple way to keep track
of the overall result there are two convenience methods added to Camera 
a) euler_angles() to return the Euler (z->x->y) rotations for the current 
orientation
b) matrix_from_two_vecors() to return the rotation matrix required to move
from a starting direction to the current direction vector, such a process
might be required to correct 'dead reckoning' from gyro readings with a
magnetometer vector.  
"""

import math,random

import demo
import pi3d

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(w=1200, h=600, frames_per_second=30)
DISPLAY.set_background(0.4,0.8,0.8,1)      # r,g,b,alpha
# yellowish directional light blueish ambient light
pi3d.Light(lightpos=(1, -1, -3), lightcol=(1.0, 1.0, 0.8), lightamb=(0.25, 0.2, 0.3))
CAMERA = pi3d.StereoCam(separation=-0.5, interlace=0)
""" If CAMERA is set with interlace <= 0 (default) then CAMERA.draw() will produce
two images side by side (each viewed from `separation` apart) i.e. -ve
requires viewing slightly cross-eyed.

If interlace is set to a positive value then the two images are interlaced
in vertical stripes this number of pixels wide. The resultant image needs
to be viewed through a grid. See https://github.com/pi3d/pi3d_demos/make_grid.py
"""

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
mytrees1.cluster(treemodel1.buf[0], mymap, 0.0, 0.0, 400.0, 400.0, 50, "", 8.0, 3.0)
mytrees1.set_draw_details(flatsh, [tree2img], 0.0, 0.0)
mytrees1.set_fog(*TFOG)

mytrees2 = pi3d.MergeShape(name="trees2")
mytrees2.cluster(treemodel2.buf[0], mymap, 0.0, 0.0, 400.0, 400.0, 80, "", 6.0, 3.0)
mytrees2.set_draw_details(flatsh, [tree1img], 0.0, 0.0)
mytrees2.set_fog(*TFOG)

mytrees3 = pi3d.MergeShape(name="trees3")
mytrees3.cluster(treemodel2, mymap,0.0, 0.0, 300.0, 300.0, 20, "", 4.0, 2.0)
mytrees3.set_draw_details(flatsh, [hb2img], 0.0, 0.0)
mytrees3.set_fog(*TFOG)

#Create monument
monument = pi3d.Model(file_string="models/pi3d.obj", name="monument")
monument.set_shader(shinesh)
monument.set_normal_shine(bumpimg, 16.0, reflimg, 0.4)
monument.set_fog(*FOG)
monument.translate(100.0, -mymap.calcHeight(100.0, 235) + 12.0, 235.0)
monument.scale(10.0, 10.0, 10.0)
monument.rotateToY(-115)

#screenshot number
scshots = 1

#avatar camera
rot = 0.0
tilt = 0.0
roll = 0.0001 # to trick the camera update first time through loop before mouse movement
avhgt = 3.5
xm = 0.0
zm = 0.0
ym = mymap.calcHeight(xm, zm) + avhgt

# Fetch key presses
mykeys = pi3d.Keyboard()
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()

start_vector = CAMERA.camera_3d.get_direction()

# Display scene and rotate cuboid
while DISPLAY.loop_running():
  l_or_k_pressed = False # to stop routine camera movement for cases where l or k pressed
  #Press ESCAPE to terminate
  mx, my = mymouse.position()
  buttons = mymouse.button_status()
  k = mykeys.read()
  if k >-1: # or buttons > mymouse.BUTTON_UP:
    dx, dy, dz = CAMERA.get_direction()
    if k == 119 or buttons == mymouse.LEFT_BUTTON:  #key W
      xm += dx
      zm += dz
      ym = mymap.calcHeight(xm, zm) + avhgt
    elif k == 115: # or buttons == mymouse.RIGHT_BUTTON:  #kry S
      xm -= dx
      zm -= dz
      ym = mymap.calcHeight(xm, zm) + avhgt
    elif k == ord('a'):
      roll += 2.0
    elif k == ord('d'):
      roll -= 2.0
    elif k == ord('l'):
      rx, ry, rz = CAMERA.camera_3d.euler_angles()
      CAMERA.move_camera((xm, ym, zm), ry, rx, rz) # default to absolute rotations
      print(rx, ry, rz)
      l_or_k_pressed = True
    elif k == ord('k'):
      vector = CAMERA.get_direction()
      if start_vector is not None:
        CAMERA.camera_3d.r_mtrx = CAMERA.camera_3d.matrix_from_two_vecors(start_vector, vector)
        ''' The above process will not preserve the z axis rotation compare
        with the following system
        _, _, rz = CAMERA.camera_3d.euler_angles() # get Euler z rotation
        rx, ry, _ = CAMERA.camera_3d.euler_angles( # get required x and y rotations to align vectors.
                        CAMERA.camera_3d.matrix_from_two_vecors(start_vector, vector))
        CAMERA.move_camera((xm, ym, zm), ry, rx, rz)'''
        print(CAMERA.camera_3d.r_mtrx)
        l_or_k_pressed = True
    elif k == ord('m'): # for this to work there needs to be an alteration to the application of the rotation matrix above
      start_vector = CAMERA.get_direction()
    elif k == 112:  #key P
      pi3d.screenshot("forestWalk"+str(scshots)+".jpg")
      scshots += 1
    elif k == 10:   #key RETURN
      mc = 0
    elif k == 27:  #Escape key
      mykeys.close()
      mymouse.stop()
      DISPLAY.stop()
      break

    halfsize = mapsize / 2.0
    xm = (xm + halfsize) % mapsize - halfsize # wrap location to stay on map -500 to +500
    zm = (zm + halfsize) % mapsize - halfsize

  rot, tilt = mymouse.velocity()
  rot *= -1.0
  if not l_or_k_pressed: #to stop overwriting move_camera() after pressing l
    CAMERA.move_camera((xm, ym, zm), rot, tilt, roll, absolute=False)
  rot, tilt, roll = 0.0, 0.0, 0.0
  myecube.position(xm, ym, zm)
  for i in range(2):
    CAMERA.start_capture(i)
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
    mytrees3.draw()
    mytrees2.draw()
    mytrees1.draw()
    CAMERA.end_capture(i)
  CAMERA.draw()