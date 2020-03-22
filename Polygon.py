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
''' using inkscape path tracing and a few lines of python '''
path = [[-11.2, -128.0], [-26.8, -119.4], [-40.7, -110.8], [-71.3, -90.9],
    [-78.9, -81.6], [-83.3, -70.6], [-88.6, -53.6], [-93.5, -43.0], [-98.4, -32.9],
    [-99.8, -20.6], [-97.9, -8.2], [-86.3, 8.8], [-82.8, 12.9], [-80.4, 22.6],
    [-76.3, 36.6], [-67.0, 48.5], [-60.2, 55.1], [-65.6, 59.4], [-73.0, 65.9],
    [-83.6, 81.0], [-89.4, 95.0], [-90.4, 106.6], [-89.1, 116.9], [-84.7, 119.5],
    [-79.7, 121.3], [-49.7, 128.0], [-28.0, 126.0], [-20.0, 123.0], [-15.1, 120.8],
    [-8.9, 115.9], [-2.2, 106.6], [1.5, 101.5], [4.4, 105.6], [11.1, 115.1],
    [18.0, 120.8], [22.9, 123.0], [41.8, 127.6], [64.7, 126.6], [74.9, 124.1],
    [82.7, 121.2], [87.6, 119.5], [91.5, 118.0], [90.4, 91.2], [89.3, 87.7],
    [86.9, 81.9], [84.5, 77.1], [75.2, 66.0], [63.0, 55.6], [59.9, 54.4],
    [65.5, 49.4], [75.6, 36.8], [80.3, 19.4], [82.3, 14.6], [87.3, 8.6],
    [95.8, -3.0], [99.8, -15.8], [99.2, -28.8], [93.9, -41.3], [89.0, -51.8],
    [86.4, -64.7], [83.7, -75.3], [78.4, -85.0], [71.0, -93.1], [61.8, -99.1],
    [49.9, -105.8], [39.4, -111.7], [28.3, -119.0], [17.2, -126.2]]

edge_path = [[i[0], i[1], 1.0] for i in path] # make copy in 3D for edges

''' Polygon '''
poly = pi3d.Polygon(path=path, z=5)
poly.set_draw_details(shader, [tex], umult=5, vmult=-5) # NB vmult -ve to flip texture

''' Lines for edges '''
edges = pi3d.PolygonLines(camera=camera, vertices=edge_path, closed=True, line_width=5.0, z=-1.0)
edges.set_material((0.0, 0.0, 0.0))
edges.set_shader(lineshader)
''' or try using texture and uv_flat shader '''
#tex2 = pi3d.Texture("textures/PATRN.PNG")
#edges.set_draw_details(shader, [tex2])

''' add edges as child of poly '''
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