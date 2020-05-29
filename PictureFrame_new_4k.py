#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' Simplified slideshow system using ImageSprite and without threading for background
loading of images (so may show delay for v large images).
'''

import demo
import pi3d
import numpy as np
import ctypes
import time
import os
import random
from multiprocessing import Process
from multiprocessing.sharedctypes import RawArray, RawValue
from PIL import Image

W, H = 1024, 512 # NB for RPi this has to divide up into permitted texture widths
AR = float(W) / H # screen aspect ratio
HW, HH = W // 2, H // 2
PSNS = [[0, 0, HW, HH],
        [HW, 0, W - HW, HH],
        [0, HH, HW, H - HH],
        [HW, HH, W - HW, H - HH]]
'''PSNS = [[0, 0, HW, H],
        [HW, 0, W - HW, H]]'''
N = (1 << (len(PSNS) + 1)) - 1
DIR = '/home/patrick/python/pi3d_demos/textures'
TMDELAY = 5.0
DA = 0.02 # delta alpha

def screen(x, y, w, h, arr, flag, a, id): # id zero based ie 0,1,2,3
    display = pi3d.Display.create(x=x, y=y, w=w, h=h, frames_per_second=23) 
    camera = pi3d.Camera(is_3d=False)
    shader = pi3d.Shader('shaders/blend_new')
    sprite = pi3d.Sprite(w=w, h=h, camera=camera)
    sprite.set_shader(shader)
    tex_arr = np.frombuffer(arr, dtype=np.uint8)
    tex_arr.shape = (H, W, 4)
    tex_bg = None
    kbd = pi3d.Keyboard()
    if id == 0:
        iFiles = []
        for f in os.listdir(DIR):
            fp = os.path.join(DIR, f)
            if os.path.isfile(fp) and ('.npg' in f or '.jpg' in f): # could also check for other types / case
                iFiles.append(fp)
        random.shuffle(iFiles)
        nFi = len(iFiles)
        pic_num = 0

        # image list stuff here
        next_tm = 0.0
    while True:
        k = kbd.read()
        if k==27: #ESC - flag quit to all processes
            flag.value = N + 1
            break #just in case this is a loop which resets flag.value!
        if flag.value == N: # OK to go TODO, no need to refresh if no change happening
            display.loop_running()
            if id == 0 and a.value < 1.0:
                a.value += DA
            sprite.unif[44] = a.value
            sprite.draw()
        if flag.value >= (N + 1): # signal to close
            break
        if id == 0: # this is the master process - only one in charge of new pictures
            tm = time.time()
            if tm > next_tm:
                next_tm = tm + TMDELAY
                flag.value = 0 # reset flag bits, freeze drawing and loading textures
                im = Image.open(iFiles[pic_num])
                if im.mode == 'RGB' or im.mode == 'RGBA': # don't cater for grayscale imgs
                    ar = float(im.size[0]) / im.size[1]
                    if ar > AR: # fit width - gap top and bottom
                        neww, newh = W, int(W / ar)
                        ew, eh = 0, int((H - newh) / 2)
                    else: # fit height - gap left and right
                        neww, newh = int(H * ar), H
                        ew, eh = int((W - neww) / 2), 0
                    im = im.resize((neww, newh))
                    tex_arr[eh:eh + newh, ew:ew + neww,:3] = np.array(im)
                    if ar > AR: # now pad top and bottom
                        tex_arr[:eh, :, :] = tex_arr[H - newh:eh:-1, :, :]
                        tex_arr[H - eh:, :, :] = tex_arr[H - eh - 1:newh - 1:-1, :, :]
                    else:
                        tex_arr[:, :ew, :] = tex_arr[:, W - neww:ew:-1, :]
                        tex_arr[:, W - ew:, :] = tex_arr[:, W - ew - 1:neww - 1: - 1, :]
                    flag.value = 1 # now OK to load textures from array
                pic_num += 1
                if pic_num >= nFi:
                    pic_num = 0
        if flag.value == (1 << (id + 1)) - 1: # need to reload this texture but has to be in correct order!
            flag.value = flag.value | (1 << (id + 1)) # set the bit for this process
            if tex_bg is not None:
                tex_bg = tex
            tex = pi3d.Texture(tex_arr[y:y + h, x:x + w, :].copy())
            if tex_bg is None: # first time only set this after new Texture loaded
                tex_bg = tex
            sprite.set_textures([tex, tex_bg])
            if id == 0:
                a.value = 0.0
        
    display.destroy()

flag = RawValue(ctypes.c_int, 0)
a = RawValue(ctypes.c_float, 0.0)
shared_arr = RawArray(ctypes.c_uint8, H * W * 4) # alternatively, Array automatically does locking in which case
tex_arr = np.frombuffer(shared_arr, dtype=np.uint8) # you need to call Array.get_obj() method here
tex_arr.shape = (H, W, 4)
tex_arr[:,:,3] = 255

for i, psns in enumerate(PSNS):
    p = Process(target=screen, args=(psns[0], psns[1], psns[2], psns[3],
                shared_arr, flag, a, i))
    p.start()

while flag.value <= N:
    time.sleep(0.2)

shared_arr = None
flag = None
a = None
