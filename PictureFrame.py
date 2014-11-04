#!/usr/bin/python

from __future__ import absolute_import, division, print_function, unicode_literals
"""This demo shows the use of special transition shaders on the Canvas 
shape for 2D drawing.
"""
import random, time, glob
# if pi3d isn't installed as a module then you will need..
import demo #which does the same as..
#import sys
#sys.path.insert(1, '/home/pi/pi3d')
import pi3d

tk = False # set to true to run in tk window (have to start x server)

def tex_load(fname):
  ''' return a slide object
  '''
  slide = Slide()
  tex = pi3d.Texture(fname, blend=True, mipmap=True)
  xrat = DISPLAY.width/tex.ix
  yrat = DISPLAY.height/tex.iy
  if yrat < xrat:
    xrat = yrat
  wi, hi = tex.ix * xrat, tex.iy * xrat
  xi = (DISPLAY.width - wi)/2
  yi = (DISPLAY.height - hi)/2
  slide.tex = tex
  slide.dimensions = (wi, hi, xi, yi)
  return slide

class Slide(object):
  def __init__(self):
    self.tex = None
    self.dimensions = None

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(background=(0.0, 0.0, 0.0, 1.0),
                                frames_per_second=20, tk=tk)
if tk:
  win = DISPLAY.tkwin
  win.update()
else:
  mykeys = pi3d.Keyboard() # don't need this for picture frame but useful for testing
 
shader = [pi3d.Shader("shaders/blend_star"),
          pi3d.Shader("shaders/blend_holes"),
          pi3d.Shader("shaders/blend_false"),
          pi3d.Shader("shaders/blend_burn"),
          pi3d.Shader("shaders/blend_bump")]
num_sh = len(shader)

iFiles = glob.glob("textures/*.*")
#iFiles = glob.glob("/home/pi/Pictures/*/*.*") # eg actual location 
iFiles.sort() # sort by name, otherwise random
nFi = len(iFiles) # number of pictures
fade_step = 0.01 # smaller number for slower transition NB MUST BE A DIVISOR OF 1.0 FOR SOME SHADERS
fade = 0.0
pic_num = nFi - 1

canvas = pi3d.Canvas()
canvas.set_shader(shader[0])

CAMERA = pi3d.Camera.instance()
CAMERA.was_moved = False #to save a tiny bit of work each loop
pictr = 0 # to allow shader changing every four slides
shnum = 0 # shader number
tmdelay = 5.0 # time between slides This needs to be big enough for texture loading and fading
nexttm = 0.0 # force next on first loop

sbg = tex_load(iFiles[pic_num]) # initially load a background slide

while DISPLAY.loop_running():
  tm = time.time()
  if tm > nexttm: # load next image
    nexttm = tm + tmdelay
    fade = 0.0 # reset fade to beginning
    sfg = sbg # foreground Slide set to old background
    pic_num = (pic_num + 1) % nFi # wraps to start
    sbg = tex_load(iFiles[pic_num]) # background Slide load.
    canvas.set_draw_details(canvas.shader,[sfg.tex, sbg.tex]) # reset two textures
    canvas.set_2d_size(sbg.dimensions[0], sbg.dimensions[1], sbg.dimensions[2], sbg.dimensions[3])
    canvas.unif[48:54] = canvas.unif[42:48] #need to pass shader dimensions for both textures
    canvas.set_2d_size(sfg.dimensions[0], sfg.dimensions[1], sfg.dimensions[2], sfg.dimensions[3])
    pictr += 1
    if pictr >= 3:# shader change only happens after 4 pictures
      pictr = 0
      shnum = (shnum + 1) % num_sh
      canvas.set_shader(shader[shnum])

  if fade < 1.0:
    fade += fade_step # increment fade
    canvas.unif[44] = fade # pass value to shader using unif list

  canvas.draw() # then draw it

  if tk:
    try:
      win.update() # needed if using tk
    except:
      DISPLAY.stop()
      try:
        win.destroy()
      except:
        pass
      break
    if win.ev == 'resized':
      DISPLAY.resize(win.winx, win.winy, win.width, win.height)
      win.resized = False
      win.ev = ''

  else:
    k = mykeys.read()
    if k==27: #ESC
      mykeys.close()
      DISPLAY.stop()
      break

DISPLAY.destroy()

