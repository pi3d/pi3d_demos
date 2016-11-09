#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Showing how the Points class can be used with its re_init() method to
generate particles. Mouse rotates camera, w key in, s key out
"""
import demo
import pi3d
import numpy as np

N = 7500      # number of sparks
DEL = 0.04    # 1/FPS i.e. time per frame
FPS = 1 / DEL # like this
F = 0.001     # initial upward velocity
R = 0.008     # random movement
A = 0.01      # air resistance
g = 0.0017    # gravity

class Sparks(pi3d.Points):
  def __init__(self, shader, tex, **kwargs):
    ''' inherit from Points class
    '''
    self.vel = np.zeros((N, 3), dtype='float32')          # velocities all zero to start
    self.verts = np.array([[0.0, -1.0, 0.0] for i in range(N)], 
                                         dtype='float32') # locations all 0,-1,0
    self.norms = np.zeros((N, 3), dtype='float32')        # normals not used
    self.texs = np.linspace(0.0, 1.0, N * 2).reshape((N, 2)) # uv coords vary with age of spark
    super(Sparks, self).__init__(vertices=self.verts, normals=self.norms, 
            tex_coords=self.texs, point_size=5, **kwargs) # pass to Points.__init__()
    self.set_draw_details(shader, [tex])

  def update(self):
    self.vel[10:] = self.vel[:-10] # 'age' all the sparks by moving along ten
    self.verts[10:] = self.verts[:-10]
    self.verts[0:10,:] = 0.0       # set new ten x,y,z to 0.0
    self.vel[0:10] = ([-0.1, 0.5, -0.1] + np.random.random((10,3)) * 
                                    [0.2, F, 0.2]) * DEL # initial up and side impulse
    ix = np.where(self.verts[:,1] > -1.0)[0]             # only move sparks when above -1.0
    self.vel[ix] += ((np.random.random((len(ix), 3)) - 0.5) * R - 
                  self.vel[ix] * self.vel[ix] * A) * DEL # turbulence and drag
    self.vel[ix,1] -= g * DEL      # gravity
    self.verts[ix] += self.vel[ix] # update positions
    self.texs[:,1] = (self.texs[:,1] + np.random.random(N) * 0.01) % 1.0 # update textures
    self.re_init(pts=self.verts, normals=self.norms, texcoords=self.texs) # re-init the buffers


display = pi3d.Display.create(background=(0.1, 0.1, 0.1, 1.0), frames_per_second=FPS)
camera = pi3d.Camera()
shader = pi3d.Shader('uv_flat')
tex = pi3d.Texture('textures/pong2.jpg')
sparks = Sparks(shader, tex) # make an instance of this class

# everything else very much as per other demos
keys = pi3d.Keyboard()
mouse = pi3d.Mouse(restrict=False)
mouse.start()

camrad = [-6.0, -6.0, -6.0]
while display.loop_running():
  rot, tilt = mouse.position()
  rot, tilt = rot * 0.1, tilt * -0.1
  camera.relocate(rot, tilt, [0.0, 0.0, 0.0], camrad)
  sparks.update()
  sparks.draw()
  k = keys.read()
  if k == 27:
    display.destroy()
    keys.close()
    break
  elif k == ord('s'): # move out
    camrad = [i * 1.05 for i in camrad]
  elif k == ord('w'): # move in
    camrad = [i * 0.95 for i in camrad]
