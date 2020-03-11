#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Sprites rendered using a diy points class and special shader uv_spriterot.

This demo builds on the SpriteBalls demo but adds sprite image rotation, thanks
to Joel Murphy on stackoverflow. The information is used by the uv_spritemult
shader as follows

  vertices[0]   x position of centre of point relative to centre of screen in pixels
  vertices[1]   y position
  vertices[2]   z depth but fract(z) is used as a multiplier for point size
  normals[0]    rotation in radians
  normals[1]    red and green values to multiply with the texture
  normals[2]    blue and alph values to multiply with the texture. The values
                are packed into the whole number and fractional parts of
                the float i.e. where R and G are between 0.0 and 0.999
                normals[:,2] = floor(999 * R) + G
  tex_coords[0] distance of left side of sprite square from left side of
                texture in uv scale 0.0 to 1.0
  tex_coords[1] distance of top of sprite square from top of texture

unif[48] is used to hold the size of the sprite square to use for texture
sampling in this case each sprite has a patch 0.125x0.125 as there
are 8x8 on the sheet. However unif[48] is set to 0.1 to leave a margin of
0.0125 around each sprite.

The movement of the vertices is calculated using numpy which makes it very
fast but it is quite hard to understand as all the iteration is done
automatically.
"""
print("""
ESC to quit
####################################################
Any key to increase temperature but..
####################################################
i key toggles interaction between bugs
s key toggles spinning or align with velocity vector
""")
import numpy as np
import random

import demo
import pi3d

MAX_BUGS = 100
MIN_BUG_SIZE = 40.0 # z value is used to determine point size
MAX_BUG_SIZE = 150.0
MAX_BUG_VELOCITY = 3.0

min_size = float(MIN_BUG_SIZE) / MAX_BUG_SIZE
max_size = 1.0

KEYBOARD = pi3d.Keyboard()

BACKGROUND_COLOR = (0.3, 0.3, 0.3, 0.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=20)
HWIDTH, HHEIGHT = DISPLAY.width / 2.0, DISPLAY.height / 2.0

CAMERA = pi3d.Camera(is_3d=False)
shader = pi3d.Shader("uv_pointsprite")

img = pi3d.Texture("textures/atlas01.png", mipmap=False, i_format=pi3d.constants.GL_RGBA,
                    filter=pi3d.constants.GL_NEAREST)
# i_format=pi3d.GL_LUMINANCE_ALPHA ## see what happens with a converted texture type
loc = np.zeros((MAX_BUGS, 3))
loc[:,0] = np.random.uniform(-HWIDTH, HWIDTH, MAX_BUGS)
loc[:,1] = np.random.uniform(-HHEIGHT, HHEIGHT, MAX_BUGS)
loc[:,2] = np.random.normal((min_size + max_size) / 2.0,
                            (max_size - min_size) / 5.0,
                            MAX_BUGS) + np.random.randint(1, 8, MAX_BUGS)
vel = np.random.uniform(-MAX_BUG_VELOCITY, MAX_BUG_VELOCITY, (MAX_BUGS, 2))

dia = (loc[:,2] % 1.0) * MAX_BUG_SIZE
mass = dia * dia
# reshape to column and transpose to make add.outer() (not yet in pypy numpy)
radii = (dia.reshape(1,-1).T + dia) / 7.0 # should be / 2.0 this will make bugs 'touch' when nearer

rot = np.zeros((MAX_BUGS, 3)) # :,0 for rotation
rot[:,1] = 999.999 # :,1 R, G
rot[:,2] = 999.999 # :,2 B, A
"""  :,2 for sub-size i.e 8x8 images each is 0.125 but there is 0.0125
margin on each side with 0.1 'useable' image inside. This is to avoid the
corners overlapping other images as they are rotated.
"""
uv = np.zeros((MAX_BUGS, 2)) # u picnum.u v
uv[:,:] = 0.0125 # all start off same. uv is top left corner of square

bugs = pi3d.Points(camera=CAMERA, vertices=loc, normals=rot, tex_coords=uv,
                   point_size=MAX_BUG_SIZE)
bugs.set_draw_details(shader, [img])
bugs.unif[48] = 0.1

temperature = 0.9
interact = True
spin = False
frame_num = 0

while DISPLAY.loop_running():
  bugs.draw()
  frame_num += 1
  ##### bounce off walls
  ix = np.where(loc[:,0] < -HWIDTH)[0] # off left side
  vel[ix,0] = np.abs(vel[ix,0]) * temperature # x component +ve
  ix = np.where(loc[:,0] > HWIDTH)[0] # off right
  vel[ix,0] = np.abs(vel[ix,0]) * -temperature # vx -ve
  ix = np.where(loc[:,1] < -HHEIGHT)[0]
  vel[ix,1] = np.abs(vel[ix,1]) * temperature
  ix = np.where(loc[:,1] > HHEIGHT)[0]
  vel[ix,1] = np.abs(vel[ix,1]) * -temperature
  vel[:,1] -= 0.01 # slight downward drift
  loc[:,0:2] += vel[:,:] # adjust x,y positions by velocities
  ##### rotate
  if spin:
    rot[:,0] += rot[:,1] * 0.4
  else: # tween towards direction of travel
    rot[:,0] +=  ((np.arctan2(vel[:,1], vel[:,0]) + 1.571 - rot[:,0])
                        % 6.283 - 3.142) * 0.2
  ##### re_init
  bugs.buf[0].re_init(pts=loc, normals=rot, texcoords=uv) # reform opengles array_buffer
  ##### trend towards net cooling
  temperature = temperature * 0.99 + 0.009 # exp smooth towards 0.9


  ##### bounce off each other. Work increases as square of N
  if interact:
    d1 = (loc[np.newaxis,:,0].T - loc[:,0]) # array of all the x diffs
    d2 = (loc[np.newaxis,:,1].T - loc[:,1]) # array of all the y diffs
    ix = np.where(((d1 ** 2 + d2 ** 2) ** 0.5 - radii) < 0.0) # index of all overlaps
    non_dup = np.where(ix[0] < ix[1])[0] # remove double count and 'self' overlaps
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
    delta1y = -1.0 * R * delta2y # other ball using mass ratio
    delta1x = -1.0 * R * D * delta2y
    vel[ix[0],0] += delta1x # update velocities
    vel[ix[0],1] += delta1y
    vel[ix[1],0] += delta2x
    vel[ix[1],1] += delta2y
    # change image occasionally
    if frame_num % 10 == 0:
      uv[ix[0],:] = np.random.randint(0, 7, (ix[0].shape[0], 2)) * 0.125 + 0.0125
      rot[ix[1],2] = np.floor(rot[ix[1],2]) + np.random.uniform(0.5, 1.0, len(ix[1]))

  k = KEYBOARD.read()
  if k > -1:
    temperature *= 1.05
    vel *= np.random.uniform(1.01, 1.03, vel.shape)
    if k == ord('i'):
      interact = not interact
    if k == ord('s'):
      spin = not spin
    if k == 27:
      KEYBOARD.close()
      DISPLAY.stop()
      break


