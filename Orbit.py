#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Model gravitational attraction between bodies. Uses a Planet class to
tidy code
"""
import numpy as np
import math
#from numpy import sqrt, sin, cos, radians, pi, add, subtract, array, tile
import demo
import pi3d

##################################################################
# Planet  class based on a pi3d.Sphere but with some added properties
class Planet(pi3d.Sphere):
  def __init__(self, textures, shader, radius, density, pos=[0.0, 0.0, 0.0],
              vel=[0.0, 0.0, 0.0], acc=[0.0, 0.0, 0.0], track_shader=None,
              light=None):
    """arguments generally self explanatory; textures is a list of Textures
    if more than one then a shell sphere is created with a slightly faster
    rotational speed, if track_shader is passed then a trace_shape is
    generated and drawn as points every 1200 call of the position_and_draw()
    method.
    
    The code for the trace_shape is a little obscure. Basically it saves
    the position of the Planet in a list of vertex (x,y,z) tuples and adds
    dummy normal and texture coordinates because there is no way to create
    a Buffer without (at the moment this will be addressed in future)
    """
    super(Planet, self).__init__(radius=radius, slices=24, sides=24,
                                 x=pos[0], y=pos[1], z=pos[2])
    super(Planet, self).set_draw_details(shader, [textures[0]])
    if light is not None:
      self.set_light(light)
    self.pos = np.array(pos)
    self.vel = np.array(vel)
    self.acc = np.array(acc)
    self.mass = math.pi * 4.0 / 3.0 * density * radius ** 3.0
    self.rotation = -0.1 / radius
    self.shell = None
    if len(textures) > 1: # second Texture for 'shell' sphere
      self.shell = pi3d.Sphere(radius=radius*1.05, slices=24, sides=24)
      self.shell.set_draw_details(shader, [textures[1]])
      if light is not None:
        self.shell.set_light(light)
      self.shell.rotation = self.rotation * 1.5
    self.track_shader = track_shader
    if track_shader is not None:
      pts = np.tile(self.pos, (750, 1)) #start off all inside planet!
      self.track = pi3d.Lines(material=(0.0,1.0,1.0), vertices=pts)
      self.f = 0 # frame counter for trail
    self.t_v, self.t_n, self.t_t, self.t_f = [], [], [], []
    self.t_len = 0 
    
  def pull(self, bodies):
    """ bodies is an array of other Planets 
    assume method is called once per DT of time (G adjusted accordingly!)
    Using numpy arrays and functions makes this vector algebra very tidy!
    This method is seperate from position_and_draw to allow DT to be finer
    grained than the frame rate. Hopefully this will reduce the error of
    approximating real life to a series of steps.
    """
    force = np.array([0.0, 0.0, 0.0])
    for body in bodies:
      dirctn = body.pos - self.pos
      dist = ((dirctn ** 2.0).sum()) ** 0.5
      """ NB dist is cubed because (dirctn/dist) is the unit vector between
      masses and the size of the force is GMm/d^2
      """
      force += dirctn * (G * self.mass * body.mass / (dist ** 3.0))

    self.acc = force / self.mass
    self.vel += self.acc * DT
    self.pos += self.vel * DT
    
  def position_and_draw(self):
    self.position(*self.pos)
    self.rotateIncY(self.rotation)
    self.draw()
    if self.shell is not None:
      self.shell.position(*self.pos)
      self.shell.rotateIncY(self.shell.rotation)
      self.shell.draw()
    if self.track_shader is not None:
      self.track.draw(self.track_shader)
      self.f += 1
      if self.f > 2:
        b = self.track.buf[0] # short cut pointer to reduce typing
        b.array_buffer[1:, 0:3] = b.array_buffer[:-1,0:3] # shunt them back one
        b.array_buffer[0, 0:3] = self.pos # add this location
        b.re_init(pts=b.array_buffer[:, 0:3])
        self.f = 0


G = 0.0000001
DT = 0.01

# Setup display and initialise pi3d ------
DISPLAY = pi3d.Display.create(x=50, y=50, frames_per_second=20)
DISPLAY.set_background(0,0,0,1)    	# r,g,b,alpha
# Camera ---------------------------------
CAMERA = pi3d.Camera()
# Shaders --------------------------------
shader = pi3d.Shader("uv_light")
flatsh = pi3d.Shader("uv_flat")
tracksh = pi3d.Shader("mat_flat")
# Textures -------------------------------
cloudimg = pi3d.Texture("textures/earth_clouds.png",True)
sunimg = pi3d.Texture("textures/sun.jpg")
sunshellimg = pi3d.Texture("textures/sun_shell.png", True)
earthimg = pi3d.Texture("textures/world_map.jpg")
moonimg = pi3d.Texture("textures/moon.jpg")
# EnvironmentCube ------------------------
ectex = [pi3d.Texture('textures/ecubes/skybox_grimmnight.jpg')]
myecube = pi3d.EnvironmentCube(size=900.0, maptype='CROSS')
myecube.set_draw_details(flatsh, ectex)
# Lights ---------------------------------
sunlight = pi3d.Light(is_point=True, lightpos=(0, 0, 0), # from the sun
          lightcol=(100.0, 100.0, 100.0), lightamb=(0.05, 0.05, 0.05))
selflight = pi3d.Light(lightamb=(1.1, 1.1, 1.1)) # on the sun
# Planets --------------------------------
sun = Planet([sunimg, sunshellimg], shader, 1.0, 8000000, pos=[0.0, 0.0, 0.0],
            vel=[-0.01, 0.0, 0.0], light=selflight) #to keep total momentum of system zero!
earth = Planet([earthimg, cloudimg], shader, 0.125, 80000000, pos=[0.0, -1.0, -9.0], 
            vel=[0.5, 0.1, 0.0], track_shader=tracksh, light=sunlight)
moon = Planet([moonimg], shader, 0.025, 80000000, pos=[0.0, -1.0, -9.6], 
            vel=[0.72, 0.144, 0.0], track_shader=tracksh, light=sunlight)
jupiter = Planet([moonimg, sunshellimg], shader, 0.2, 8000000,  pos=[0.0, 0.0, 14.0],
            vel=[-0.2, 0.3, 0.0], track_shader=tracksh, light=sunlight)
# Fetch key presses ----------------------
mykeys = pi3d.Keyboard()
# Mouse ----------------------------------
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()
omx, omy = mymouse.position()
# Camera variables -----------------------
rot = 0
tilt = 0
rottilt = True
camRad = 13.5
# Display scene
while DISPLAY.loop_running():
  if rottilt:
    CAMERA.reset()
    CAMERA.rotate(-tilt, rot, 0)
    CAMERA.position((camRad * math.sin(math.radians(rot)) * math.cos(math.radians(tilt)), 
                     camRad * math.sin(math.radians(tilt)), 
                    -camRad * math.cos(math.radians(rot)) * math.cos(math.radians(tilt))))
    rottilt = False
  for i in range(5): # make time interval for physics fifth of frame time
    sun.pull([earth, moon, jupiter])
    earth.pull([sun, moon, jupiter])
    moon.pull([sun, earth, jupiter])
    jupiter.pull([sun, earth, moon])
  sun.position_and_draw()
  earth.position_and_draw()
  moon.position_and_draw()
  jupiter.position_and_draw()
  myecube.draw()

  mx, my = mymouse.position()
  if mx != omx or my != omy:
    rot -= (mx - omx) * 0.1
    tilt -= (my - omy) * 0.1
    omx, omy = mx, my
    rottilt = True

  k = mykeys.read()
  if k >-1:
    rottilt = True
    if k==112:
      pi3d.screenshot("orbit.jpg")
    elif k==119:  #key W rotate camera up
      tilt += 2.0
    elif k==115:  #kry S down
      tilt -= 2.0
    elif k==97:   #key A left
      rot -= 2
    elif k==100:  #key D right
      rot += 2
    elif k==61:   #key += in
      camRad -= 0.5
    elif k==45:   #key _- out
      camRad += 0.5
    elif k==27:
      mykeys.close()
      DISPLAY.destroy()
      break

