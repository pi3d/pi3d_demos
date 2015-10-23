#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" An example of making objects change shape by re-creating them inside the while loop
the textures are also offset by a different amount each frame.
"""
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

# code originally came from a forum:http://gamedev.stackexchange.com/questions/23625/how-do-you-generate-tileable-perlin-noise
# suggestion by boojum.
class Noise3D():
  # initialize class with the grid size (inSize), frequency (inFreq) and number of octaves (octs) 
  def __init__(self, size, freq, octs, seed=1):
    self.perm = [i for i in range(256)]
    random.seed(seed)
    random.shuffle(self.perm)
    self.perm += self.perm
    self.dirs = [(cos(a * 2.0 * pi / 256),
                  cos((a+85) * 2.0 * pi / 256),
                  cos((a+170) * 2.0 * pi / 256))
                  for a in range(256)]
    self.size = size
    self.freq = freq
    self.octs = octs

  def noise(self, x, y, per):
    def surflet(gridX, gridY):
      distX, distY = abs(x-gridX), abs(y-gridY)
      polyX = 1 - 6 * distX**5 + 15 * distX**4 - 10 * distX**3
      polyY = 1 - 6 * distY**5 + 15 * distY**4 - 10 * distY**3
      hashed = self.perm[self.perm[self.perm[int(gridX) % per] + int(gridY) % per]]
      grad = (x - gridX)*self.dirs[hashed][0] + (y - gridY)*self.dirs[hashed][1]
      return polyX * polyY * grad
        
    intX, intY = int(x), int(y)
    return (surflet(intX + 0, intY + 0) + surflet(intX + 0, intY + 1) +
            surflet(intX + 1, intY + 0) + surflet(intX + 1, intY + 1))

  #return a value for noise in 2D
  def generate(self, x, y):
    val = 0
    x = x * self.freq
    y = y * self.freq
    per = int(self.freq * self.size)
    for o in range(self.octs):
      val += 0.5**o * self.noise(x * 2**o, y * 2**o, per * 2**o)
    return val

DISPLAY = pi3d.Display.create(x=50, y=50, frames_per_second=20,
                  background=(0.6, 0.5, 0.0, 1.0))

opengles.glDisable(GL_CULL_FACE) # do this as it will be possible to look under terrain, has to done after Display.create()

shader = pi3d.Shader("mat_light")
flatsh = pi3d.Shader("mat_flat")

perlin = Noise3D(PSIZE, PFREQ, POCT) # size of grid, frequency of noise,
# number of octaves, use 5 octaves as reasonable balance

#### generate terrain
verts = []
norms = []
tex_coords = []
idx = []
wh = hh = W / 2.0 # half size
ws = hs = W / (IX - 1.0) # dist between each vert
tx = tz = 1.0 / IX

for z in range(IZ):
  for x in range(IX):
    this_x = -wh + x*ws
    this_z = -hh + z*hs
    ht = perlin.generate(x, z) * HT
    verts.append([this_x, ht, this_z])

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

xoff, zoff = 0, 0

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
      s1, s2, s3, s4, s5, s6, s7, s8, s9 = 1, IXZ, 1,   0, IXZ - 1,   1, 0, IXZ, IX
      newedge = [perlin.generate(xoff, (z + zoff) % PSIZE) * HT for z in range(IZ)]
      flg = True
    elif k == ord("s"):
      xoff = (xoff + 1) % PSIZE
      s1, s2, s3, s4, s5, s6, s7, s8, s9 = 0, IXZ - 1, 1,   1, IXZ, 1,   IX - 1, IXZ, IX
      newedge = [perlin.generate(xoff + IX - 1, (z + zoff) % PSIZE) * HT for z in range(IZ)]
      flg = True
    elif k == ord("z"):
      zoff = (zoff - 1) % PSIZE
      s1, s2, s3, s4, s5, s6, s7, s8, s9 = IZ, IXZ, 1,   0, IXZ - IZ, 1,   0, IZ, 1
      newedge = [perlin.generate((x + xoff) % PSIZE, zoff) * HT for x in range(IX)]
      flg = True
    elif k == ord("a"):
      zoff = (zoff + 1) % PSIZE
      s1, s2, s3, s4, s5, s6, s7, s8, s9 = 0, IXZ - IZ, 1,   IZ, IXZ, 1,   IXZ - IZ, IXZ, 1
      newedge = [perlin.generate((x + xoff) % PSIZE, zoff + IZ - 1) * HT for x in range(IX)]
      flg = True

    if flg: # i.e. one of above keys pressed
      b = terrain.buf[0]
      b.array_buffer[s1:s2:s3,1] = b.array_buffer[s4:s5:s6,1]
      b.array_buffer[s7:s8:s9,1] = newedge
      b.array_buffer[:,3:6] = b.calc_normals()
      b.re_init(pts=b.array_buffer[:,0:3], normals = b.array_buffer[:,3:6])

