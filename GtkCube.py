#!/usr/bin/python

import demo
import pi3d
import threading
import time
import gtk
import gtk.gdk as gdk
''' For gtk to work with python 3 you need to have installed gi
sudo apt-get install python3-gi
then instead of 'import gtk' 
import gi
from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GdkPixbuf
However I couldn't get the new_from_data() function to work to work

Also, when running on ubuntu laptop the pixel copying often has patterns of
'holes' and there are occasional serious error (seg faults) when closing
the application. Any further help with this would be appreciated!
'''
W, H = 640, 480

''' This system works by copying the pi3d screen image and 'pasting' it
onto a gtk image.

NB to get the pi3d layer 'behind' the X windows you need to set its
value to < -127
'''
DISPLAY = pi3d.Display.create(w=W, h=H, frames_per_second=20, layer=-128)
shader = pi3d.Shader('uv_light')
tex = pi3d.Texture('textures/PATRN.PNG')

cube = pi3d.Cuboid(z=2)
cube.set_draw_details(shader, [tex])
cube.show_flag = True # additional attribute stuck onto Cuboid instance
cube.last_x = None
cube.last_y = None

def rotX(widget, cube):
  cube.rotateIncX(5.0)
  cube.show_flag = True

def rotY(widget, cube):
  cube.rotateIncY(15.0)
  cube.show_flag = True

def rotZ(widget, cube):
  cube.rotateIncZ(20.0)
  cube.show_flag = True

def close_app(widget, data):
  DISPLAY.destroy()
  win.destroy()
  gtk.main_quit()
  quit(0)

def mot(widget, ev, cube):
  if ev.is_hint:
    x, y, st = ev.window.get_pointer()
  else :
    x, y, st = ev.x, ev.y, ev.state
  if st & gtk.gdk.BUTTON1_MASK :
    if cube.last_x is None:
      cube.last_x = x
      cube.last_y = y
    cube.rotateIncY(cube.last_x - x)
    cube.rotateIncX(cube.last_y - y)
    cube.last_x = x
    cube.last_y = y
    cube.show_flag = True
  else:
    cube.last_x = None
    cube.last_y = None

win = gtk.Window()
win.set_title('GTK minimal demo')
win.connect('delete_event', close_app)

box1 = gtk.HBox(False, 0)
win.add(box1)
box2 = gtk.VBox(False, 0)
box1.pack_start(box2, True, True, 1)

image_box = gtk.EventBox()
box1.add(image_box)
img_flag = 0
img_gtk = gtk.Image()  # Create gtk.Image() only once
image_box.add(img_gtk) # Add Image in the box, only once

button1 = gtk.Button('Rotate X 5deg')
button1.connect('clicked', rotX, cube)
box2.pack_start(button1, True, True, 0)
button2 = gtk.Button('Rotate Y 15deg')
button2.connect('clicked', rotY, cube)
box2.pack_start(button2, True, True, 0)
button3 = gtk.Button('Rotate Z 20deg')
button3.connect('clicked', rotZ, cube)
box2.pack_start(button3, True, True, 0)
message = gtk.Label('Left click and\ndrag on image or\nclick these buttons')
message.set_justify(gtk.JUSTIFY_CENTER)
box2.pack_start(message, True, True, 5)

image_box.connect("motion_notify_event", mot, cube)
image_box.set_events(gtk.gdk.EXPOSURE_MASK
                    |gtk.gdk.LEAVE_NOTIFY_MASK
                    |gtk.gdk.BUTTON_PRESS_MASK
                    |gtk.gdk.POINTER_MOTION_MASK
                    |gtk.gdk.POINTER_MOTION_HINT_MASK)

box1.show()
box2.show()
win.show_all()

''' gtk needs to run in its own thread to allow the pi3d drawing to happen
    at the same time'''
gdk.threads_init()
t = threading.Thread(target=gtk.main, name='GTK thread')
t.daemon = True
t.start()

while DISPLAY.loop_running():
  if cube.show_flag:
    cube.draw()
    img_gtk.set_from_pixbuf(gtk.gdk.pixbuf_new_from_array(
                              pi3d.screenshot(), gtk.gdk.COLORSPACE_RGB, 8))
    ''' see note above about python 3
    img_gtk.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_data(pi3d.screenshot(), 
                        GdkPixbuf.Colorspace.RGB, True, 8, W, H, W * 4)) '''
    win.show_all()
    cube.show_flag = False

