#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" An example of making objects change shape by re-creating them inside the while loop
the textures are also offset by a different amount each frame.
"""
import numpy as np
from math import sin, cos, radians, pi
import random
import demo
import pi3d
from pi3d import opengles, GL_CULL_FACE

IX = IZ = 64 # number of verts in x and z dir
IXZ = IX * IZ # to save a bit of time with numpy slices later
W = D = 10.0 # width and depth
HT = 4.0 # height scale of terrain
PSIZE = 128 # perlin size
PFREQ = 1.0 / 32.0 # perlin frequency
POCT = 5 # perlin octaves
CAMRAD = 15.0 # radius of camera position
ALL = slice(None, None) # slice all in this dimension

# code originally came from a forum:http://gamedev.stackexchange.com/questions/23625/how-do-you-generate-tileable-perlin-noise
# suggestion by boojum.
class Noise3D():
  # initialize class with the grid size (inSize), frequency (inFreq) and number of octaves (octs) 
  def __init__(self, size, freq, octs, seed=1):
    perm = [i for i in range(256)]
    random.seed(seed)
    random.shuffle(perm)
    perm += perm
    self.perm = np.array(perm)
    self.dirs = np.array([[cos(a * 2.0 * pi / 256),
                  cos((a + 85) * 2.0 * pi / 256),
                  cos((a + 170) * 2.0 * pi / 256)]
                  for a in range(256)])
    self.size = size
    self.freq = freq
    self.octs = octs

  def noise(self, xy, per):
    """ xy is 3D array of x,y values as floats 
    """
    def surflet(gridXY):
      distXY = np.absolute(xy - gridXY)
      polyXY = 1.0 - 6.0 * distXY**5 + 15.0 * distXY**4 - 10.0 * distXY**3
      hashed = self.perm[
                self.perm[
                  self.perm[gridXY[:,:,0].astype(np.int) % per] +
                            gridXY[:,:,1].astype(np.int) % per]]
      grad = ((xy[:,:,0] - gridXY[:,:,0]) * self.dirs[hashed][:,:,0] +
              (xy[:,:,1] - gridXY[:,:,1]) * self.dirs[hashed][:,:,1])
      return polyXY[:,:,0] * polyXY[:,:,1] * grad
        
    intXY = xy.astype(np.int)
    return (surflet(intXY + [0, 0]) + surflet(intXY + [0, 1]) +
            surflet(intXY + [1, 0]) + surflet(intXY + [1, 1]))

  #return a value for noise in 2D
  def generate(self, xy):
    """ xy is 3D array of x,y values 
    """
    val = np.zeros(xy.shape[:2]) # ie same x,y dimensions
    xy = np.array(xy, dtype=np.float) * self.freq
    per = int(self.freq * self.size)
    for o in range(self.octs):
      val += 0.5**o * self.noise(xy * 2**o, per * 2**o)
    return val

DISPLAY = pi3d.Display.create(x=50, y=50, frames_per_second=20,
                  background=(0.6, 0.5, 0.0, 1.0))

opengles.glDisable(GL_CULL_FACE) # do this as it will be possible to look under terrain, has to done after Display.create()

shader = pi3d.Shader("mat_light")
flatsh = pi3d.Shader("mat_flat")

perlin = Noise3D(PSIZE, PFREQ, POCT) # size of grid, frequency of noise,
# number of octaves, use 5 octaves as reasonable balance

#### generate terrain
norms = []
tex_coords = []
idx = []
wh = hh = W / 2.0 # half size
ws = hs = W / (IX - 1.0) # dist between each vert
tx = tz = 1.0 / IX

verts = np.zeros((IZ, IX, 3), dtype=np.float) # c order arrays 
xy = np.array([[[x, y] for x in range(IX)] for y in range(IZ)])
verts[:,:,0] = xy[:,:,0] * ws - wh
verts[:,:,2] = xy[:,:,1] * hs - hh
verts[:,:,1] = perlin.generate(xy) * HT # y value perlin noise height
verts.shape = (IZ * IX, 3) # pi3d uses semi-flattened arrays

s = 0
#create one long triangle_strip by alternating X directions
for z in range(0, IZ-1):
  for x in range(0, IX-1):
    i = (z * IX) + x
    idx.append([i, i + IX, i + IX + 1])
    idx.append([i + IX + 1, i + 1, i])
    s += 2

terrain = pi3d.Shape(None, None, "terrain", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                      1.0, 1.0, 1.0, 0.0, 0.0, 0.0)
terrain.buf = []
terrain.buf.append(pi3d.Buffer(terrain, verts, tex_coords, idx, None, True))
terrain.set_material((0.2,0.3,0.5))
terrain.set_shader(shader)

axes = pi3d.Lines(vertices=[[2.0*W, 0.0, 0.0], [0.0, 0.0, 0.0],
                  [0.0, 2.0*HT, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 2.0*D]],
                  line_width=3, x=-W/2.0, z=-D/2.0)
axes.set_shader(flatsh)

mouserot = 0.0 # rotation of camera
tilt = 15.0 # tilt of camera
frame = 0

#key presses
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()
omx, omy = mymouse.position()

xoff, yoff, zoff = 0, 0, 0

mykeys = pi3d.Keyboard()
CAMERA = pi3d.Camera.instance()

# main display loop
while DISPLAY.loop_running():
  mx, my = mymouse.position() # camera can move around object with mouse move
  mouserot -= (mx-omx)*0.2
  tilt -= (my-omy)*0.1
  omx=mx
  omy=my
  CAMERA.reset()
  CAMERA.rotate(-tilt, mouserot, 0)
  CAMERA.position((CAMRAD * sin(radians(mouserot)) * cos(radians(tilt)), 
                   CAMRAD * sin(radians(tilt)), 
                   -CAMRAD * cos(radians(mouserot)) * cos(radians(tilt))))

  terrain.draw()
  axes.draw()

  k = mykeys.read()
  if k > -1:
    flg = False
    if k == 27:
      mykeys.close()
      mymouse.stop()
      DISPLAY.destroy()
      break
    elif k == ord("x"):
      xoff = (xoff - 1) % PSIZE
      s1,s2, s3, s4 = ALL, slice(1, None), ALL, slice(None, -1)
      s5, s6 = ALL, slice(None, 1)
      newedge = [[[xoff, (z + zoff) % PSIZE]] for z in range(IZ)]
      flg = True
    elif k == ord("s"):
      xoff = (xoff + 1) % PSIZE
      s1,s2, s3, s4 = ALL, slice(None, -1), ALL, slice(1, None)
      s5, s6 = ALL, slice(-1, None)
      newedge = [[[xoff + IX - 1, (z + zoff) % PSIZE]] for z in range(IZ)]
      flg = True
    elif k == ord("z"):
      zoff = (zoff - 1) % PSIZE
      s1,s2, s3, s4 = slice(1, None), ALL, slice(None, -1), ALL
      s5, s6 = slice(None, 1), ALL
      newedge = [[[(x + xoff) % PSIZE, zoff] for x in range(IX)]]
      flg = True
    elif k == ord("a"):
      zoff = (zoff + 1) % PSIZE
      s1,s2, s3, s4 = slice(None, -1), ALL, slice(1, None), ALL
      s5, s6 = slice(-1, None), ALL
      newedge = [[[(x + xoff) % PSIZE, zoff + IZ - 1] for x in range(IX)]]
      flg = True

    if flg: # i.e. one of above keys pressed
      newedge = perlin.generate(np.array(newedge)) * HT
      b = terrain.buf[0]
      bab = b.array_buffer # aliases to reduce typing
      bab.shape = (IZ, IX, 6)
      bab[s1,s2,1] = bab[s3,s4,1]
      bab[s5,s6,1] = newedge
      bab.shape = (IZ * IX, 6)
      bab[:,3:6] = b.calc_normals()
      b.re_init(pts=bab[:,0:3], normals = bab[:,3:6])

