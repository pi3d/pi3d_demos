#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import math, random, time, traceback, os
import sys
import demo
import pi3d
from six_mod import unichr # have to do this after importing pi3d as it's part of package

# use tab for backspace and carriage return for delete
CHARS = {'space':' ', 'BackSpace':'\t', 'DEL':'\r', 'Return':'\n',
         unichr(263):'\t', unichr(330):'\r'}
"""for some reason these last two are the codes returned by this keyboard
using curses on the raspberry pi (for BackSpace and DEL - you might need 
to fine tune this look-up dictionary system
"""

def cbx(*args):
  if radio.clicked:
    menu1.show()
  else:
    menu1.hide()

def cb(*args):
  print(args)

class scroll_cb(object):
  def __init__(self, callback, delta):
    self.callback = callback
    self.delta = delta

  def roty(self, *args):
    print(args)
    slideval = args[0] * self.delta
    self.callback(slideval)
  
class jogger(object):
  "jogger class"
  def __init__(self, gui, label, x, y, callback, delta) :
    self.callback = callback
    self.delta = delta
    self.x = x
    self.y = y
    self.butP = pi3d.Button(gui, "l.gif", x, y, label=label,
                                        shortcut='d', callback=self.rotp)
    self.butM = pi3d.Button(gui, "r.gif", x + 32, y, shortcut='l',
                                        callback=self.rotm)

  def rotp(self, *args):
    self.callback(self.delta)

  def rotm(self, *args):
    self.callback(-self.delta)

DISPLAY = pi3d.Display.create(x=50, y=50, w=640, h=480, frames_per_second=30)
DISPLAY.set_background(0.8,0.8,0.8,1.0) # r,g,b,alpha

shader = pi3d.Shader("uv_reflect")
font = pi3d.Font("fonts/NotoSans-Regular.ttf", color=(0,0,0,255), font_size=20)
gui = pi3d.Gui(font)
ww, hh = DISPLAY.width / 2.0, DISPLAY.height / 2.0

img = pi3d.Texture("textures/rock1.jpg")
model = pi3d.Cuboid(z=5.0)
model.set_draw_details(shader, [img])

radio = pi3d.Radio(gui, ww -20, hh - 32,
                label="unhides menu!", label_pos="left", callback=cbx)
xi = -ww
yi = hh
for b in ['tool_estop.gif', 'tool_power.gif', 'tool_open.gif']:
  #       'tool_reload.gif', 'tool_run.gif', 'tool_step.gif',
  #       'tool_pause.gif', 'tool_stop.gif', 'tool_blockdelete.gif',
  #       'tool_optpause.gif', 'tool_zoomin.gif', 'tool_zoomout.gif',
  #       'tool_axis_z.gif', 'tool_axis_z2.gif', 'tool_axis_x.gif',
  #       'tool_axis_y.gif', 'tool_axis_p.gif', 'tool_rotate.gif',
  #       'tool_clear.gif']: 
  """ these other images are available but 
  too many objects will be slow in python on pi - keep it lean """
  g = pi3d.Button(gui, b, xi, yi, shortcut='d', callback=cb)
  xi = xi + 32


button = pi3d.Button(gui, ["tool_run.gif", "tool_pause.gif"], ww - 40,
                -hh + 40, callback=cb, shortcut='q')
scr_cb = scroll_cb(model.rotateToY, -360) #convoluted way of avoiding global!
scrollbar = pi3d.Scrollbar(gui, -ww + 20, -hh + 20, 200, start_val=50,
                label="slide me", label_pos='above', callback=scr_cb.roty)

jog1 = jogger(gui, 'X', ww - 64, hh - 64, model.translateX, -0.1)
jog2 = jogger(gui, 'Y', ww - 64, hh - 96, model.translateY, 0.1)
jog3 = jogger(gui, 'Z', ww - 64, hh - 128, model.translateZ, 0.1)
jog4 = jogger(gui, 'Zt', ww - 64, hh - 160, model.rotateIncZ, 7)

mi1 = pi3d.MenuItem(gui,"File")
mi2 = pi3d.MenuItem(gui,"Edit")
mi3 = pi3d.MenuItem(gui,"Window")
mi11 = pi3d.MenuItem(gui, "Open")
mi12 = pi3d.MenuItem(gui, "Close")
mi111 = pi3d.MenuItem(gui, "x1", callback=cb)
mi112 = pi3d.MenuItem(gui, "x2", callback=cb)
mi121 = pi3d.MenuItem(gui, "v3", callback=cb)
mi122 = pi3d.MenuItem(gui, "v4", callback=cb)

menu1 = pi3d.Menu(parent_item=None, menuitems=[mi1, mi2, mi3],
          x=-ww, y=hh-32, visible=True)
menu2 = pi3d.Menu(parent_item=mi1, menuitems=[mi11, mi12], horiz=False, position='below')
menu3 = pi3d.Menu(parent_item=mi11, menuitems=[mi111, mi112], horiz=False, position='right')
menu4 = pi3d.Menu(parent_item=mi12, menuitems=[mi121, mi122], horiz=False, position='right')

textbox = pi3d.TextBox(gui, "type here", 100, -180, callback=cb, label='TextBox (KEY t to edit)',
                        shortcut='t')

mx, my = 0, 0
#inputs = pi3d.InputEvents()
mouse = pi3d.Mouse(use_x=True, restrict=True)
if pi3d.PLATFORM == pi3d.PLATFORM_PI:
  x_off = -DISPLAY.left - DISPLAY.width / 2
  y_off = DISPLAY.top + DISPLAY.height / 2 - DISPLAY.max_height
#inputs.get_mouse_movement()
mouse.start()
keyboard = pi3d.Keyboard()
shifted = False
caps = False

while DISPLAY.loop_running(): #and not inputs.key_state("KEY_ESC"):
  mx, my = mouse.position()
  if pi3d.PLATFORM == pi3d.PLATFORM_PI:
    mx += x_off
    my += y_off
  buttons = mouse.button_status()
  model.draw()
  gui.draw(mx, my)
  if buttons == mouse.LEFT_BUTTON:
    gui.check(mx, my)
  kc = keyboard.read_code()
  if len(kc) > 0:
    ### print(kc, ord(kc)) # for debugging key codes!
    if kc == chr(27) or kc == "Escape":
      break
    if "Shift" in kc:
      shifted = True
    elif "Caps" in kc:
      caps = not caps
    else:
      if kc in CHARS:
        this_key = CHARS[kc]
      else:
        this_key = kc
        if shifted or caps:
          this_key = this_key.upper()
        shifted = False
      gui.checkkey(this_key)

#inputs.release()
mouse.stop()
DISPLAY.destroy()
