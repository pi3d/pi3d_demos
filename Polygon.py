#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

''' Polygon class creates a mesh of triangles to fill a line, joining the last point
back to the first. Escape to quit, 'w' enlarge, 's' shrink, space makes random rgba for
the corners and edges, other key return to black.

In this demo the edges and corners are children of the polygon so their z distance is
negative to bring them nearer the camera. The mat_pointsprite shader has been used to
draw the circular points of the corners and that shader uses the decimal fraction of the
z distance to control the size.

The mat_pointsprite shader also uses the three components of the normal to represent r,g,b
for each point and the first component of the texture coordinates for the alpha. There is a
slightly more complicated demo of changing point rgba if space is pressed
'''
import demo
import pi3d
import numpy as np # only needed for the demo of random colours after pressing space

display = pi3d.Display.create(frames_per_second=60, background=(0.3, 0.3, 0.2, 0.2)) # try using samples=4
shader = pi3d.Shader('uv_flat')
lineshader = pi3d.Shader('mat_flat')
pointshader = pi3d.Shader('mat_pointsprite')
tex = pi3d.Texture('textures/Raspi256x256.png')
camera = pi3d.Camera(is_3d=False)

path = [[0, -220], [-80, -200], [-170, -190], [-175, -95], [-220, 0], [-160, 75],
         [-160, 120], [-100, 140], [-240, 240], [-120, 280], [0, 200],
         [120, 280], [240, 240], [100, 140], [160, 120], [160, 75], [220, 0],
         [175, -95], [170, -190], [80, -200]]
#path = [[-200,-200], [200,200], [-200,200], [200,-200], [100, -50]] # 'bad' polygon. N.B. crossed lines not checked
edge_path = [[i[0], i[1], 0.999] for i in path] # make copy in 3D for edges and corners
# NB z values are 0.999 as decimal fraction used for dia - try changing to 1.0

''' Polygon '''
poly = pi3d.Polygon(path=path, z=5)
poly.set_draw_details(shader, [tex], umult=5, vmult=-5) # NB vmult -ve to flip texture

''' Lines for edges '''
edges = pi3d.Lines(camera=camera, vertices=edge_path, closed=True, line_width=10.0, z=-1.0)
edges.set_material((0.0, 0.0, 0.0))
edges.set_shader(lineshader)

''' Points for corners '''
corners = pi3d.Points(camera=camera, vertices=edge_path, point_size=10.0, z=-2.0)
corners.set_shader(pointshader)
corners.buf[0].unib[0] = 20.0 # this controls the hardness of the point edges

''' add edges and corners as children of poly '''
poly.add_child(edges)
poly.add_child(corners) # comment out to see what it looks like without 

kb = pi3d.Keyboard()
sc = 1.0
while display.loop_running():
  poly.draw() # only draw, rotate, scale parent Shape
  poly.rotateIncZ(0.05)
  k = kb.read()
  if k != -1:
    if k == 27:
      break
    elif k == ord('w'):
      sc *= 1.02
      poly.scale(sc, sc, sc)
    elif k == ord('s'):
      sc /= 1.02
      poly.scale(sc, sc, sc)
    else: # other key
      buf = corners.buf[0].array_buffer # alias for brevity
      if k == ord(' '): # space
        buf[:,3:6] = np.random.random((buf.shape[0], 3))
        edges.set_material(np.random.random((3,)))
      else: # back to black
        buf[:,3:6] = [0.0, 0.0, 0.0]
        edges.set_material((0.0, 0.0, 0.0))
      corners.re_init() # needed to effect the change

kb.close()
display.destroy()