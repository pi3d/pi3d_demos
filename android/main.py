#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' This demos is a re-hash of ForestWalk but constructed in a way that
allows it to be used with python-for-android and kivy. i.e. the loop part
has been put into a method of a class (unimaginatively called Main)

This results in lots of self. prefixes to the variables, but that is a
feature of python.

An additional feature that isn't in ForestWalk is that the ElevationMap
has been made seamless and saved as a png 33x33 this allows the Camera
to run from one tile to the next (it actually jumps back to the other side,
so it's always on the same tile). The colours at the edges don't match
because of lighting effects due to the way normals are calculated to smooth
maps (May be fixed at some stage...)
'''
import sys
sys.path.insert(1,'/home/pi/pi3d')
import math,random
import pi3d
import ctypes
from pi3d.constants import *

class Main(object):
  # Setup display and initialise pi3d
  DISPLAY = pi3d.Display.create()
  pi3d.Light(lightpos=(1, -1, -3), lightcol =(1.0, 1.0, 0.8), lightamb=(0.25, 0.2, 0.3))
  # load shader
  shader = pi3d.Shader("uv_bump")
  shinesh = pi3d.Shader("uv_reflect")
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
  monument = pi3d.Model(file_string="models/pi3d.obj", name="monument")
  monument.set_shader(shinesh)
  monument.set_normal_shine(bumpimg, 16.0, reflimg, 0.4)
  monument.set_fog(*FOG)
  monument.translate(100.0, -mymap.calcHeight(100.0, 235) + 12.0, 235.0)
  monument.scale(20.0, 20.0, 20.0)
  monument.rotateToY(65)

  #avatar camera
  rot = 0.0
  tilt = 0.0
  avhgt = 3.5
  xm = 0.0
  zm = 0.0
  ym = mymap.calcHeight(xm, zm) + avhgt

  go_flag = False
  go_speed = 0.2

  CAMERA = pi3d.Camera.instance()

  def pi3dloop(self, dt):
    self.DISPLAY.loop_running()
    self.CAMERA.reset()
    self.CAMERA.rotate(self.tilt, self.rot, 0)
    self.CAMERA.position((self.xm, self.ym, self.zm))
    self.myecube.position(self.xm, self.ym, self.zm)

    # for opaque objects it is more efficient to draw from near to far as the
    # shader will not calculate pixels already concealed by something nearer
    self.myecube.draw()
    self.mymap.draw()
    dx = math.copysign(self.mapsize, self.xm)
    dz = math.copysign(self.mapsize, self.zm)
    mid = 0.3 * self.mapsize
    if abs(self.xm) > mid: #nearing edge
      self.mymap.position(dx, 0.0, 0.0)
      self.mymap.draw()
    if abs(self.zm) > mid: #other edge
      self.mymap.position(0.0, 0.0, dz)
      self.mymap.draw()
      if abs(self.xm) > mid: #i.e. in corner, both edges
        self.mymap.position(dx, 0.0, dz)
        self.mymap.draw()
    self.mymap.position(0.0, 0.0, 0.0)
    self.monument.draw()
    self.mytrees1.draw()
    self.mytrees2.draw()
    self.mytrees3.draw()

    if pi3d.PLATFORM == PLATFORM_ANDROID: #*****************************
      if self.DISPLAY.android.screen.moved:
        self.rot -= self.DISPLAY.android.screen.touch.dx * 0.25
        self.tilt += self.DISPLAY.android.screen.touch.dy * 0.25
        self.DISPLAY.android.screen.moved = False
        self.DISPLAY.android.screen.tapped = False
      elif self.DISPLAY.android.screen.tapped:
        self.go_speed *= 1.5
        self.DISPLAY.android.screen.tapped = False
      elif self.DISPLAY.android.screen.double_tapped:
        self.go_flag = not self.go_flag
        self.DISPLAY.android.screen.double_tapped = False
    else:
      mx, my = self.mymouse.position()

      #if mx>display.left and mx<display.right and my>display.top and my<display.bottom:
      self.rot -= (mx - self.omx)*0.2
      self.tilt += (my - self.omy)*0.2
      self.omx = mx
      self.omy = my

      #Press ESCAPE to terminate
      k = self.mykeys.read()
      if k >-1:
        if k==ord('w'):  #key W
          self.go_flag = not self.go_flag
        elif k==27:  #Escape key
          return False

    if self.go_flag:
      self.xm -= math.sin(math.radians(self.rot)) * self.go_speed
      self.zm += math.cos(math.radians(self.rot)) * self.go_speed
      self.ym = self.mymap.calcHeight(self.xm, self.zm) + self.avhgt
      halfmap = self.mapsize / 2.0 # save doing this four times!
      self.xm = (self.xm + halfmap) % self.mapsize - halfmap
      self.zm = (self.zm + halfmap) % self.mapsize - halfmap

    else:
      self.go_speed = 0.2
    return True

  def run(self):
    if pi3d.PLATFORM == PLATFORM_ANDROID: #*****************************
      self.DISPLAY.android.set_loop(self.pi3dloop)
      self.DISPLAY.android.run()
    else:
      # Fetch key presses
      self.mykeys = pi3d.Keyboard()
      self.mymouse = pi3d.Mouse(restrict = False)
      self.mymouse.start()
      self.omx, self.omy = self.mymouse.position()
      while self.pi3dloop(0.0):
        pass
      self.mykeys.close()
      self.mymouse.stop()
        
    self.DISPLAY.stop()

Main().run() #create an instance of Main() then run the method
