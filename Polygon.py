#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

''' Polygon class creates a mesh of triangles to fill a line, joining the last point
back to the first. Escape to quit, 'w' enlarge, 's' shrink.

In this demo the edges are children of the polygon so their z distance is
negative to bring them nearer the camera.
'''
import demo
import pi3d
import numpy as np # only needed for the demo of random colours after pressing space

display = pi3d.Display.create(frames_per_second=60, background=(0.3, 0.3, 0.2, 0.2)) # try using samples=4
shader = pi3d.Shader('uv_flat')
lineshader = pi3d.Shader('mat_flat')
tex = pi3d.Texture('textures/Raspi256x256.png')
camera = pi3d.Camera(is_3d=False)

path = [[0, -220], [-80, -200], [-170, -190], [-175, -95], [-220, 0], [-160, 75],
         [-160, 120], [-100, 140], [-240, 240], [-120, 280], [0, 200],
         [120, 280], [240, 240], [100, 140], [160, 120], [160, 75], [220, 0],
         [175, -95], [170, -190], [80, -200]]
#path = [[-200,-200], [200,200], [-200,200], [200,-200], [100, -50]] # 'bad' polygon. N.B. crossed lines not checked
edge_path = [[i[0], i[1], 1.0] for i in path] # make copy in 3D for edges

''' Polygon '''
poly = pi3d.Polygon(path=path, z=5)
poly.set_draw_details(shader, [tex], umult=5, vmult=-5) # NB vmult -ve to flip texture

''' Lines for edges '''
edges = pi3d.PolygonLines(camera=camera, vertices=edge_path, closed=True, line_width=10.0, z=-1.0)
edges.set_material((0.0, 0.0, 0.0))
edges.set_shader(lineshader)

''' add edges and corners as children of poly '''
poly.add_child(edges)

kb = pi3d.Keyboard()
sc = 1.0
while display.loop_running():
  poly.draw() # only draw, rotate, scale parent Shape
  poly.rotateIncZ(0.05)
  k = kb.read()
  if k != -1:
    if k == 27:
      break
    elif k == ord('w'): # w and s scale bigger and smaller
      sc *= 1.02
      poly.scale(sc, sc, sc)
    elif k == ord('s'):
      sc /= 1.02
      poly.scale(sc, sc, sc)

kb.close()
display.destroy()