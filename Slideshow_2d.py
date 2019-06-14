#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' Simplified slideshow system using ImageSprite and without threading for background
loading of images (so may show delay for v large images).
    Also has a minimal use of PointText and TextBlock system with reduced  codepoints
and reduced grid_size to give better resolution for large characters.

    ESC to quit, 's' to reverse, any other key to move on one.
'''
import os
import time
import random
import demo
import pi3d

TMDELAY = 10.0
DA = 0.01 # delta alpha
DIR = 'textures'
FONT_FILE = 'fonts/NotoSans-Regular.ttf'

def tex_load(fname):
    tex = pi3d.Texture(fname, blend=True, m_repeat=True)
    slide = pi3d.ImageSprite(tex, shader=shader, camera=CAMERA,
                            w=DISPLAY.width, h=DISPLAY.height, z=5.0)
    slide.set_alpha(0.0)
    return slide

DISPLAY = pi3d.Display.create(background=(0.0, 0.0, 0.0, 1.0), frames_per_second=27)

shader = pi3d.Shader("uv_flat")
CAMERA = pi3d.Camera(is_3d=False)
kbd = pi3d.Keyboard()

# images in iFiles list
nexttm = 0.0
iFiles = []
for f in os.listdir(DIR):
    fp = os.path.join(DIR, f)
    if os.path.isfile(fp): # could also check for type
        iFiles.append(fp)
random.shuffle(iFiles)
nFi = len(iFiles)
pic_num = 0
sfg = tex_load(iFiles[pic_num])

# PointText and TextBlock
font = pi3d.Font(FONT_FILE, codepoints=' 0123456789.s#', grid_size=4, shadow_radius=4.0,
                 font_size=200, shadow=(0,0,0,128))
text = pi3d.PointText(font, CAMERA, max_chars=50, point_size=200)
textblock = pi3d.TextBlock(x=-DISPLAY.width * 0.5 + 50, y=0,
                           z=0.1, rot=0.0, char_count=15,
                           text_format="{:5.2f}s #{}".format(time.time() % 1000.0, pic_num), size=0.99, 
                           spacing="M", space=1.1, colour=(1.0, 1.0, 1.0, 1.0))

text.add_text_block(textblock)

while DISPLAY.loop_running():
    tm = time.time()
    if tm > nexttm: # this must run first iteration of loop
        nexttm = tm + TMDELAY
        a = 0.0
        sbg = sfg
        sbg.positionZ(10.0)
        pic_num += 1
        if pic_num >= nFi:
            random.shuffle(iFiles)
            pic_num = 0
        sfg = tex_load(iFiles[pic_num])

    if a < 1.0:
        a += DA
        sbg.draw() # background only needs to be drawn if fg alpha < 1
    sfg.set_alpha(a)
    sfg.draw()

    textblock.set_text(text_format="{:5.2f}s #{}".format(time.time() % 1000.0, pic_num))
    text.regen()
    text.draw()

    k = kbd.read()
    if k != -1:
        nexttm = time.time() - 1.0
    if k==27: #ESC
        break
    if k==ord('s'): # go back a picture
        pic_num -= 2
        if pic_num < -1:
            pic_num = -1

kbd.close()
DISPLAY.destroy()
