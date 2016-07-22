#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' This demos is a re-hash of ForestWalk but constructed in a way that
allows it to be used with python-for-android and kivy. i.e. the loop part
has been put into a method of a class (unimaginatively called Main)

This results in lots of self. prefixes to the variables, but that is a
feature of python.

The w key toggles movement rather than each press moving a unit distance
and on android a tap does the same thing. Steering is with the mouse on
computer and with touch-move on android.
'''
import demo
import math,random
import pi3d
import ctypes

TILT_F = 0.002
SLOPE_F = 0.01
FRICTION = 0.99
OFFSET = 8.0

class Main(object):
  # Setup display and initialise pi3d
  DISPLAY = pi3d.Display.create(depth=16)
  pi3d.Light(lightpos=(1, -1, -3), lightcol =(1.0, 1.0, 0.8), lightamb=(0.25, 0.2, 0.3))
  # load shader
  shader = pi3d.Shader("uv_bump")
  shinesh = pi3d.Shader("uv_reflect")
  flatsh = pi3d.Shader("uv_flat")
  
  bumpimg = pi3d.Texture("textures/grasstile_n.jpg")
  reflimg = pi3d.Texture("textures/stars.jpg")
  rockimg = pi3d.Texture("textures/rock1.jpg")

  FOG = ((0.3, 0.3, 0.4, 0.8), 650.0)

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

  #Create monument
  monument = pi3d.Model(file_string="models/pi3d.obj", name="monument")
  monument.set_shader(shinesh)
  monument.set_normal_shine(bumpimg, 16.0, reflimg, 0.4)
  monument.set_fog(*FOG)
  monument.translate(100.0, -mymap.calcHeight(100.0, 235) + 12.0, 235.0)
  monument.scale(20.0, 20.0, 20.0)
  monument.rotateToY(65)

  #Ball
  ball = pi3d.Triangle(corners=((-0.01,0.0),(0.0,0.01),(0.01,0.0)))
  sphere = pi3d.Sphere()
  sphere.set_draw_details(shader, [rockimg, bumpimg], 1.0)
  ball.add_child(sphere)

  #avatar camera
  rot = 0.0
  tilt = 0.0
  avhgt = 1.0
  xm = 0.0
  zm = 0.0
  ym = mymap.calcHeight(xm, zm) + avhgt

  go_flag = False
  vx, vz = 0.0, 0.0
  gx, gz = 0.0, 0.0

  CAMERA = pi3d.Camera.instance()
  CAMERA2D = pi3d.Camera(is_3d=False)
  font = pi3d.Pngfont("fonts/GillSansMT.png", (200, 30, 10, 255))
  font.blend = True
  txt = None
  
  if pi3d.PLATFORM == pi3d.PLATFORM_ANDROID: #*****************************
    from jnius import autoclass
    Hardware = autoclass(b'org.renpy.android.Hardware')
    Hardware.accelerometerEnable(True)

  def pi3dloop(self, dt):
    self.DISPLAY.loop_running()
    self.CAMERA.relocate(self.rot, self.tilt, [self.xm, self.ym, self.zm], 
                                              [-OFFSET, -OFFSET, -OFFSET])
    self.myecube.position(self.xm, self.ym, self.zm)
    self.ball.position(self.xm, self.ym, self.zm)

    # for opaque objects it is more efficient to draw from near to far as the
    # shader will not calculate pixels already concealed by something nearer
    self.ball.draw()
    self.mymap.draw()
    self.myecube.draw()
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

    if pi3d.PLATFORM == pi3d.PLATFORM_ANDROID: #*****************************
      if self.DISPLAY.android.screen.moved:
        self.rot -= self.DISPLAY.android.screen.touch.dx * 0.25
        self.tilt += self.DISPLAY.android.screen.touch.dy * 0.25
        self.DISPLAY.android.screen.moved = False
        self.DISPLAY.android.screen.tapped = False
      elif self.DISPLAY.android.screen.double_tapped:
        self.go_flag = not self.go_flag
        self.DISPLAY.android.screen.double_tapped = False
        from kivy.network.urlrequest import UrlRequest
        def url_success(req, results):
          self.txt = pi3d.String(camera=self.CAMERA2D, font=self.font, string=results,
                        is_3d=False, y=self.DISPLAY.height / 2.0 + 30.0)
          self.txt.set_shader(self.flatsh)
          self.monument.rotateIncY(4) # rotate by some random amount
        req = UrlRequest("http://www.eldwick.org.uk/files/rogo/test2.php?num=1", url_success)
      if self.txt is not None:
        self.txt.draw()
        (x, y, z) = self.Hardware.accelerometerReading()
        sr, _, cr = self.CAMERA.get_direction()
        self.gx = y * cr + (z - x) * sr
        self.gz = (z - x) * cr - y * sr # i.e. hold at 45 degrees for neutral
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
        sr, _, cr = self.CAMERA.get_direction()
        if k==ord('w'):  #key W
          self.go_flag = not self.go_flag
        elif k == 261 or k == 137: # rgt
          self.gx += 0.5 * cr
          self.gz -= 0.5 * sr
        elif k == 260 or k == 136: # lft
          self.gx -= 0.5 * cr
          self.gz += 0.5 * sr
        elif k == 259 or k == 134: # up
          self.gz += 0.5 * cr
          self.gx += 0.5 * sr
        elif k == 258 or k == 135: # dwn
          self.gz -= 0.5 * cr
          self.gx -= 0.5 * sr
        elif k==27:  #Escape key
          return False

    if self.go_flag:
      self.xm += self.vx
      self.zm += self.vz
      ht, norm = self.mymap.calcHeight(self.xm, self.zm, True)
      self.ym =  ht + self.avhgt
      self.vx += norm[0] * SLOPE_F + self.gx * TILT_F
      self.vz += norm[2] * SLOPE_F + self.gz * TILT_F
      self.vx *= FRICTION
      self.vz *= FRICTION
      self.ball.rotateToY(math.degrees(math.atan2(self.vx, self.vz)))
      self.sphere.rotateIncX(math.degrees((self.vx ** 2 + self.vz ** 2) ** 0.5))
      halfmap = self.mapsize / 2.0 # save doing this four times!
      self.xm = (self.xm + halfmap) % self.mapsize - halfmap
      self.zm = (self.zm + halfmap) % self.mapsize - halfmap

    else:
      self.vx = 0.0
      self.vz = 0.0
      self.gx = 0.0
      self.gz = 0.0
    return True

  def run(self):
    if pi3d.PLATFORM == pi3d.PLATFORM_ANDROID: #*****************************
      self.DISPLAY.android.set_loop(self.pi3dloop)
      self.DISPLAY.android.run()
      self.Hardware.accelerometerEnable(False)
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
