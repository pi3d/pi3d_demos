#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Example showing use of FixedString. ESC to quit

FixedString should be faster for rendering large quantities of text as
it only requires two triangles for the whole text rather than two triangles
for each letter"""
import demo
import pi3d

DISPLAY = pi3d.Display.create(x=150, y=150, frames_per_second=30)
flatsh = pi3d.Shader("uv_flat")
shader = pi3d.Shader("uv_bump")
CAMERA = pi3d.Camera()
CAMERA2D = pi3d.Camera(is_3d=False)
pi3d.Light(lightpos=(10, -10, 2))
tex = pi3d.Texture('textures/rock1.jpg')
mytext = '''Pi3D is a Python module that
aims to greatly simplify
writing 3D in Python whilst
giving access to the power
of the Raspberry Pi GPU.
It enables both 3D and 2D
rendering and aims to provide
a host of exciting commands.'''
# 'normal' FixedString on a (fairly) solid background
str1 = pi3d.FixedString('fonts/NotoSans-Regular.ttf', mytext, font_size=32, 
                        background_color=(200,140,20,235),
                        camera=CAMERA2D, shader=flatsh, f_type='SMOOTH')
str1.sprite.position(-300, 0, 2) #NB note Shape methods act on FixedString.sprite
# shadow outline FixedString to show up against light or dark backgrounds
# try setting shadow_radius to 0 to see what the issue is
str1a = pi3d.FixedString('fonts/NotoSans-Regular.ttf', mytext[:53], font_size=48, 
                        color=(70, 70, 180, 255), background_color=None, shadow_radius=1, 
                        camera=CAMERA2D, shader=flatsh, f_type='SMOOTH')
str1a.sprite.position(50, -150, 1) #NB note Shape methods act on FixedString.sprite

str2 = pi3d.FixedString('fonts/NotoSerif-Regular.ttf', mytext, font_size=24, f_type='BUMP')
mycuboid = pi3d.Cuboid(camera=CAMERA, z=2, x=0.5)
mycuboid.set_draw_details(shader, [tex, str2], 1.0, 0.0)
#following is a bit low level but makes it fit nicely look in docs to see
#how Buffer.unib[6 and 7] control mapping uv to object
mycuboid.buf[0].unib[6] = str2.sprite.buf[0].unib[6]
mycuboid.buf[0].unib[7] = str2.sprite.buf[0].unib[7]

mykeys = pi3d.Keyboard()
while DISPLAY.loop_running():
  str1.draw()
  mycuboid.draw()
  str1a.draw()
  mycuboid.rotateIncX(0.091)
  mycuboid.rotateIncY(0.13)
  if mykeys.read() == 27:
    mykeys.close()
    DISPLAY.destroy()
    break
