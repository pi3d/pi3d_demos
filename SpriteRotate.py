#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Sprites rendered using the Points class and special shader uv_sprite
This is intended for use with an orthographic camera rather than the
perspective camera used to control point size in the other shaders.

The movement of the vertices is calculated using numpy which makes it very
fast but it is quite hard to understand as all the iteration is done
automatically.
"""
print("""
ESC to quit
Any key to increase temperature but..
i key toggles interaction between balls

""")
import numpy as np

import demo
import pi3d

MAX_BALLS = 6000
MIN_BALL_SIZE = 15 # z value is used to determine point size
MAX_BALL_SIZE = 75
MAX_BALL_VELOCITY = 3.0

min_dist = 1.001
max_dist = 0.001 + float(MAX_BALL_SIZE) / MIN_BALL_SIZE

KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log.logger(__name__)

BACKGROUND_COLOR = (0.0, 0.0, 0.0, 0.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR)
HWIDTH, HHEIGHT = DISPLAY.width / 2.0, DISPLAY.height / 2.0

CAMERA = pi3d.Camera(is_3d=False)
shader = pi3d.Shader("shaders/uv_spriterot")

ballimg = pi3d.Texture("textures/raspi_rot.png")

loc = np.zeros((MAX_BALLS, 3))
loc[:,0] = np.random.uniform(-HWIDTH, HWIDTH, MAX_BALLS)
loc[:,1] = np.random.uniform(-HHEIGHT, HHEIGHT, MAX_BALLS)
loc[:,2] = np.random.uniform(min_dist, max_dist, MAX_BALLS)
vel = np.random.uniform(-MAX_BALL_VELOCITY, MAX_BALL_VELOCITY, (MAX_BALLS, 2))
dia = (MIN_BALL_SIZE + (max_dist - loc[:,2]) /
                (max_dist - min_dist) * (MAX_BALL_SIZE - MIN_BALL_SIZE))
mass = dia * dia
radii = np.add.outer(dia, dia) / 3.0 # should be / 2.0 this will make balls 'touch' when nearer

rot = np.zeros((MAX_BALLS, 3)) # :,0 for rotation, :,1 for speed of rot
rot[:,1] = np.random.uniform(-0.1, 0.1, MAX_BALLS) # all start at 0.0

#balls = pi3d.Points(vertices=loc, point_size=MAX_BALL_SIZE)
balls = pi3d.Shape(CAMERA, None, "points", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                1.0, 1.0, 1.0, 0.0, 0.0, 0.0)
indices = [(a, a + 1, a + 2) for a in range(0, MAX_BALLS, 3)]
balls.buf = [pi3d.Buffer(balls, loc, [], indices, rot, smooth=False)]
balls.set_point_size(MAX_BALL_SIZE)
balls.set_draw_details(shader, [ballimg])

temperature = 0.9
interact = False

while DISPLAY.loop_running():
  balls.draw()
  ##### bounce off walls
  ix = np.where(loc[:,0] < -HWIDTH) # off left side
  vel[ix,0] = np.abs(vel[ix,0]) * temperature # x component +ve
  ix = np.where(loc[:,0] > HWIDTH) # off right
  vel[ix,0] = np.abs(vel[ix,0]) * -temperature # vx -ve
  ix = np.where(loc[:,1] < -HHEIGHT)
  vel[ix,1] = np.abs(vel[ix,1]) * temperature
  ix = np.where(loc[:,1] > HHEIGHT)
  vel[ix,1] = np.abs(vel[ix,1]) * -temperature
  vel[:,1] -= 0.01 # slight downward drift
  loc[:,0:2] += vel[:,:] # adjust x,y positions by velocities
  ##### rotate
  rot[:,0] += rot[:,1]
  ##### re_init
  balls.buf[0].re_init(pts=loc, normals=rot) # reform opengles array_buffer
  ##### trend towards net cooling
  temperature = temperature * 0.99 + 0.009 # exp smooth towards 0.9


  ##### bounce off each other. Work increases as square of N
  if interact:
    d1 = np.subtract.outer(loc[:,0], loc[:,0]) # array of all the x diffs
    d2 = np.subtract.outer(loc[:,1], loc[:,1]) # array of all the y diffs
    ix = np.where((np.hypot(d1, d2) - radii) < 0.0) # index of all overlaps
    non_dup = np.where(ix[0] < ix[1]) # remove double count and 'self' overlaps
    ix = (ix[0][non_dup], ix[1][non_dup]) # remake slimmed down index
    dx = d1[ix[0], ix[1]] # separation x component
    dy = d2[ix[0], ix[1]] # sep y
    D = dx / dy # component ratio
    R = mass[ix[1]] / mass[ix[0]] # mass ratio
    # minor fudge factor to stop them sticking to each other if dx or dy == 0
    delta2y = 2 * (D * vel[ix[0],0] + vel[ix[0],1] -
                   D * vel[ix[1],0] - vel[ix[1],1]) / (
                  (1.0 + D * D) * (R + 1)) * temperature - dy * 0.01
    delta2x = D * delta2y - dx * 0.01 # x component from direction
    delta1y = -1.0 * R * delta2y # other ball using mass ration
    delta1x = -1.0 * R * D * delta2y
    vel[ix[0],0] += delta1x # update velocities
    vel[ix[0],1] += delta1y
    vel[ix[1],0] += delta2x
    vel[ix[1],1] += delta2y

  k = KEYBOARD.read()
  if k > -1:
    temperature *= 1.05
    vel *= np.random.uniform(1.01, 1.03, vel.shape)
    if k == ord('i'):
      interact = not interact
    if k == 27:
      KEYBOARD.close()
      DISPLAY.stop()
      break


