#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Example showing what can be left out. ESC to quit"""
import demo
import pi3d
import math
from pi3d.constants import GL_ALPHA, GL_LUMINANCE, GL_LUMINANCE_ALPHA, GL_RGB, GL_RGBA
DISPLAY = pi3d.Display.create()
W, H = DISPLAY.width / 4, DISPLAY.height / 4
shader = pi3d.Shader("uv_flat")
CAMERA = pi3d.Camera()

gl_formats = [None, GL_ALPHA, GL_LUMINANCE, GL_LUMINANCE_ALPHA, GL_RGB, GL_RGBA]
files = ['lenna_l.png', 'lenna_la.png', 'lenna_rgb.png', 'lenna_rgba.png']
startx = -5 * W / 12
posy = 3 * H / 8
dx = W / 6
dy = -H / 4
w = W / 6
h = H / 4
sprites = []
for f in files:
  posx = startx
  for gf in gl_formats:
    s = pi3d.ImageSprite(pi3d.Texture('textures/' + f, mipmap=False, i_format=gf), 
                         shader, w=w, h=h, z=500.0, x=posx, y=posy)
    posx += dx
    sprites.append(s)

  posy += dy

bkgsprite = pi3d.ImageSprite('textures/PATRN.PNG', shader, w=W*2, h=H*2, z=630.0)

mykeys = pi3d.Keyboard()
t = 0.0
while DISPLAY.loop_running():
  bkgsprite.draw()
  t += 0.005
  for i,s in enumerate(sprites):
    s.positionZ(250.0 * (1.5 + math.sin(t)))
    s.set_material((math.sin(t*1.02 - i*0.02) * 0.5 + 0.5, 
                    math.sin(t*0.73 - i*0.03) * 0.5 + 0.5, 
                    math.sin(t*0.67 + i*0.02) * 0.5 + 0.5))
    s.draw()

  if mykeys.read() == 27:
    mykeys.close()
    DISPLAY.destroy()
    break
