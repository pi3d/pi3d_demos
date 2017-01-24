#!/usr/bin/python

from __future__ import absolute_import, division, print_function, unicode_literals

from math import tan, radians
import random, time, fnmatch, os, threading
import demo
import pi3d

from six_mod.moves import queue

def interp(x, xp, yp):
  for i, val in enumerate(xp):
    if x < val:
      if i == 0:
        return val
      else:
        return yp[i-1] + (yp[i] - yp[i-1]) * (x - xp[i-1]) / float(xp[i] - xp[i-1])
  return yp[-1]

print("""#########################################################
press ESC to escape
lft/up rgt/dwn = back, next slide
pgdn   pgup    = forward 10, back 10
+/=    -/_     = increase magnification, reduce magnification
1-5    6-0     = speed up, slow down
#########################################################""")
# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(background=(0.0, 0.0, 0.0, 1.0), frames_per_second=40)
shader = pi3d.Shader("uv_flat")

CAMERA = pi3d.Camera()

iFiles = []
for root, dirnames, filenames in os.walk("textures/"):
  for filename in fnmatch.filter(filenames, '*.[jJ][pP][gG]'):
      iFiles.append(os.path.join(root, filename))
iFiles.sort()
nFi = len(iFiles)
fileQ = queue.Queue() # queue for loading new texture files

alpha_step = 0.05
nSli = 8
drawFlag = False

NSTEPS = 300.0
TSTEPS = [0.0, 0.35, 1.0]
ZSTEPS = [0.0, 1.0, 1.0]
YSTEPS = [0.0, -1.0, 1.0]
PAUSE = 1.0
MAG = 250

def tex_load():
  while True:
    item = fileQ.get()
    # reminder, item is [filename, target Slide]
    fname = item[0]
    slide = item[1]
    #block until all the dawing is done TBD
    #tex = pi3d.Texture(item[0], mipmap=False) #pixelly but faster 3.3MB in 3s
    tex = pi3d.Texture(fname, blend=True, mipmap=True) #nicer but slower 3.3MB in 4.5s
    rat = 1.0 * DISPLAY.width / tex.ix / DISPLAY.height * tex.iy
    if rat > 1.0:
      rat = 1.0
    rat *= 1000.0 * tan(radians(CAMERA.lens[2] / 2.0))
    wi, hi = tex.ix / tex.iy * rat, rat
    slide.set_draw_details(shader,[tex])
    slide.scale(wi, hi, 1.0)
    slide.set_alpha(0)
    fileQ.task_done()

class Slide(pi3d.Sprite):
  def __init__(self):
    super(Slide, self).__init__(w=1.0, h=1.0)
    self.visible = False
    self.fadeup = False
    self.active = False
    self.steps = 0
    self.dstep = 1.0

class Carousel:
  def __init__(self, start_at=0):
    self.slides = [None] * nSli
    half = 0
    for i in range(nSli):
      self.slides[i] = Slide()
    for i in range(nSli):
      # never mind this, hop is just to fill in the first series of images from
      # inside-out: 4 3 5 2 6 1 7 0.
      half += (i % 2)
      step = (1, -1)[i % 2]
      hop = 4 + step*half

      self.slides[hop].positionZ(500.8 - (hop/10.0))
      item = [iFiles[(hop + start_at) % nFi], self.slides[hop % nSli]]
      fileQ.put(item)

    self.focus = 3 # holds the index of the focused image
    self.focus_fi = 0 # the file index of the focused image
    self.slides[self.focus].visible = True
    self.slides[self.focus].fadeup = True

  def next(self, step=1):
    self.slides[self.focus].fadeup = False
    self.focus = (self.focus + step) % nSli
    self.focus_fi = (self.focus_fi + step)%nFi
    # the focused slide is set to z = 0.1.
    # further away as i goes to the left (and wraps)
    for i in range(nSli):
      self.slides[(self.focus-i)%nSli].positionZ(0.1*i + 499.1)
      self.slides[(self.focus-i)%nSli].positionY(0.0)
      self.slides[(self.focus-i)%nSli].positionX(0.0)
    self.slides[self.focus].fadeup = True
    self.slides[self.focus].visible = True

    item = [iFiles[(self.focus_fi + 4) % nFi], self.slides[(self.focus - 4) % nSli]]
    fileQ.put(item)

  def prev(self, step=1):
    self.slides[self.focus].fadeup = False
    self.focus = (self.focus - step) % nSli
    self.focus_fi = (self.focus_fi - step) % nFi
    for i in range(nSli):
      self.slides[(self.focus-i)%nSli].positionZ(0.1*i + 499.1)
      self.slides[(self.focus-i)%nSli].positionY(0.0)
      self.slides[(self.focus-i)%nSli].positionX(0.0)
    self.slides[self.focus].fadeup = True
    self.slides[self.focus].visible = True

    item = [iFiles[(self.focus_fi-3)%nFi], self.slides[(self.focus+5)%nSli]]
    fileQ.put(item)

  def update(self):
    # for each slide check the fade direction, bump the alpha and clip
    for i in range(nSli):
      a = self.slides[i].alpha()
      if self.slides[i].fadeup == True:
        if a < 1:
          a += alpha_step
          self.slides[i].set_alpha(a)
          self.slides[i].visible = True
          self.slides[i].active = True
          self.slides[i].step = 0
        else:
          if self.slides[i].step > NSTEPS:
            self.slides[i].dstep = -1.0
          elif self.slides[i].step < 0:
            self.slides[i].dstep = 1.0
            self.next()
          self.slides[i].step += self.slides[i].dstep * PAUSE
          self.slides[i].positionZ(500.0 - (500.0 - MAG) *
                  interp(self.slides[i].step / NSTEPS, TSTEPS, ZSTEPS))
          self.slides[i].positionY((500.0 - MAG) / 2.5 *
                  interp(self.slides[i].step / NSTEPS, TSTEPS, YSTEPS))
      elif self.slides[i].fadeup == False and a > 0:
        a -= alpha_step
        self.slides[i].set_alpha(a)
        self.slides[i].visible = True
        self.slides[i].active = True
      else:
        if a <= 0:
          self.slides[i].visible = False
        self.slides[i].active = False

  def draw(self):
    # slides have to be drawn back to front for transparency to work.
    # the 'focused' slide by definition at z=0.1, with deeper z
    # trailing to the left.  So start by drawing the one to the right
    # of 'focused', if it is set to visible.  It will be in the back.
    for i in range(nSli):
      ix = (self.focus+i+1)%nSli
      if self.slides[ix].visible == True:
        self.slides[ix].draw()


crsl = Carousel()

t = threading.Thread(target=tex_load)
t.daemon = True
t.start()

# block the world, for now, until all the initial textures are in.
# later on, if the UI overruns the thread, there will be no crashola since the
# old texture should still be there.
fileQ.join()

# Fetch key presses
mykeys = pi3d.Keyboard()
CAMERA = pi3d.Camera.instance()
CAMERA.was_moved = False #to save a tiny bit of work each loop


while DISPLAY.loop_running():
  crsl.update()
  crsl.draw()

  k = mykeys.read()
  #k = -1
  if k >-1:
    if k==27: #ESC
      mykeys.close()
      DISPLAY.stop()
      break
    # left arrow go back a picture
    elif k==134 or k==136:
      crsl.prev()
    # pgdn go forward 10 pictures
    elif k==133:
      crsl.next(10)
    # pgup go back 10 pictures
    elif k==130:
      crsl.prev(10)
    # + increase magnification
    elif k==61:
      MAG /= 1.25
    # - decrease magnification
    elif k==45:
      MAG *= 1.25
    # 1to5 slow down
    elif k >= 49 and k <= 53: 
      NSTEPS *= 1.25
    # 6to0 speed up
    elif (k >= 54 and k <= 57) or k==48:
      NSTEPS /= 1.25
    # p or space pause
    elif k==112 or k==32:
      PAUSE = (PAUSE + 1) % 2
    #all other keys load next picture
    else:
      crsl.next()
    print(crsl.focus_fi, iFiles[crsl.focus_fi])

DISPLAY.destroy()

