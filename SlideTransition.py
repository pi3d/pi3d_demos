#!/usr/bin/python

from __future__ import absolute_import, division, print_function, unicode_literals

"""This demo shows the use of special transition shaders on the Canvas 
shape for 2D drawing. Also threading is used to allow the file access to 
be done in the background.
"""
import random, time, glob, threading
import demo
import pi3d

from six_mod.moves import queue

LOGGER = pi3d.Log(__name__, level='INFO', format='%(message)s')
LOGGER.info('''#########################################################
press ESC to escape, S to go back, any key for next slide
#########################################################''')

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(background=(0.0, 0.0, 0.0, 1.0), frames_per_second=20)
shader = [pi3d.Shader("shaders/blend_holes"),
          pi3d.Shader("shaders/blend_false"),
          pi3d.Shader("shaders/blend_burn"),
          pi3d.Shader("shaders/blend_bump")]

iFiles = glob.glob("textures/*.*")
iFiles.sort()
nFi = len(iFiles)
fileQ = queue.Queue() # queue for loading new texture files

fade_step = 0.025
nSli = 8

def tex_load():
  """ This function runs all the time in a background thread. It checks the
  fileQ for images to load that have been inserted by Carousel.next() or prev()

  here the images are scaled to fit the Display size, if they were to be
  rendered pixel for pixel as the original then the mipmap=False argument would
  be used, which is faster, and w and h values set to the Texture size i.e.

  tex = pi3d.Texture(f, mipmap=False)
  ...
  wi, hi = tex.ix, tex.iy

  mipmap=False can also be used to speed up Texture loading and reduce the work
  required of the cpu
  """
  while True:
    item = fileQ.get()
    fname = item[0] #nicer to use these aliases
    slide = item[1]
    #tex = pi3d.Texture(item[0], blend=True, mipmap=False) #pixelly but faster 3.3MB in 3s
    tex = pi3d.Texture(fname, blend=True, mipmap=True) #nicer but slower 3.3MB in 4.5s
    xrat = DISPLAY.width/tex.ix
    yrat = DISPLAY.height/tex.iy
    if yrat < xrat:
      xrat = yrat
    wi, hi = tex.ix * xrat, tex.iy * xrat
    #wi, hi = tex.ix, tex.iy
    xi = (DISPLAY.width - wi)/2
    yi = (DISPLAY.height - hi)/2
    slide.tex = tex
    slide.dimensions = (wi, hi, xi, yi)
    fileQ.task_done()

class Slide(object):
  def __init__(self):
    self.tex = None
    self.dimensions = None

class Carousel:
  def __init__(self):
    self.canvas = pi3d.Canvas()
    self.canvas.set_shader(shader[0])
    self.fade = 0.0
    self.slides = [None]*nSli
    half = 0
    for i in range(nSli):
      self.slides[i] = Slide()
    for i in range(nSli):
      item = [iFiles[i % nFi], self.slides[i % nSli]]
      fileQ.put(item)

    self.focus = nSli - 1
    self.focus_fi = nFi - 1

  def next(self, step=1):
    self.fade = 0.0
    sfg = self.slides[self.focus] #foreground
    self.focus = (self.focus + step) % nSli
    self.focus_fi = (self.focus_fi + step) % nFi
    sbg = self.slides[self.focus] #background
    self.canvas.set_draw_details(self.canvas.shader,[sfg.tex, sbg.tex])
    self.canvas.set_2d_size(sbg.dimensions[0], sbg.dimensions[1], sbg.dimensions[2], sbg.dimensions[3])
    self.canvas.unif[48:54] = self.canvas.unif[42:48] #need to pass shader dimensions for both textures
    self.canvas.set_2d_size(sfg.dimensions[0], sfg.dimensions[1], sfg.dimensions[2], sfg.dimensions[3])
    # get thread to put one in end of pipe
    item = [iFiles[(self.focus_fi + int(0.5 + 3.5 * step)) % nFi], self.slides[(self.focus + int(0.5 - 4.5 * step)) % nSli]]
    fileQ.put(item)
    #fileQ.join() 
    ''' for picture frame app you probably dont need background thread 
    for loading textures - it could just be a normal function called in
    series. You can simulate this (in a rather convoluted way) by
    uncommenting the join() above
    '''

  def prev(self):
    self.next(step=-1)

  def update(self):
    if self.fade < 1.0:
      self.fade += fade_step
    
  def draw(self):
    self.canvas.unif[44] = self.fade
    self.canvas.draw()

crsl = Carousel()

t = threading.Thread(target=tex_load)
t.daemon = True
t.start()

# block the world, for now, until all the initial textures are in.
# later on, if the UI overruns the thread, there will be no crashola since the
# old texture should still be there.
fileQ.join()

crsl.next() # use to set up draw details for canvas
crsl.fade = 1.0 # so doesnt transition to slide #1

# Fetch key presses
mykeys = pi3d.Keyboard()
CAMERA = pi3d.Camera.instance()
CAMERA.was_moved = False #to save a tiny bit of work each loop
pictr = 0 #to do shader changing
shnum = 0
lasttm = time.time()
tmdelay = 8.0

while DISPLAY.loop_running():
  crsl.update()
  crsl.draw()
  tm = time.time()
  if tm > (lasttm + tmdelay):
    lasttm = tm
    crsl.next()

  k = mykeys.read()
  #k = -1
  if k >-1:
    pictr += 1
    if pictr > 3:#shader change only happens after 4 button presses (ie not auto changes)
      pictr = 0
      shnum = (shnum + 1) % 4
      crsl.canvas.set_shader(shader[shnum])
    if k==27: #ESC
      mykeys.close()
      DISPLAY.stop()
      break
    if k==115: #S go back a picture
      crsl.prev()
    #all other keys load next picture
    else:
      crsl.next()

DISPLAY.destroy()

