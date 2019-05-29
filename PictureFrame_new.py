#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' Simplified slideshow system using ImageSprite and without threading for background
loading of images (so may show delay for v large images).
    Also has a minimal use of PointText and TextBlock system with reduced  codepoints
and reduced grid_size to give better resolution for large characters.
    Also shows a simple use of MQTT to control the slideshow parameters remotely
see http://pi3d.github.io/html/FAQ.html and https://www.thedigitalpictureframe.com/control-your-digital-picture-frame-with-home-assistents-wifi-presence-detection-and-mqtt/
and https://www.cloudmqtt.com/plans.html

    ESC to quit, 's' to reverse, any other key to move on one.
'''
import os
import time
import random
import demo
import pi3d
import paho.mqtt.client as mqtt

from PIL import Image, ExifTags # these are needed for getting exif data from images

#####################################################
# these variables are constants
#####################################################
#PIC_DIR = '/home/patrick/Pictures/2019/image_sequence/test1' #'textures'
PIC_DIR = '/home/pi/pi3d_demos/textures' #'textures'
FPS = 20
FONT_FILE = 'fonts/NotoSans-Regular.ttf'
CODEPOINTS = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ., _-/' # limit to 49 ie 7x7 grid_size
#####################################################
# these variables can be altered using mqtt messaging
#####################################################
time_delay = 10.0 # between slides
fade_time = 3.0
shuffle = True # shuffle on reloading
check_num = 200 # number to show before reshuffling
date_from = None
date_to = None
quit = False

delta_alpha = 1.0 / (FPS * fade_time) # delta alpha

#####################################################
# some functions to tidy subsequent code
#####################################################
def tex_load(fname):
    tex = pi3d.Texture(fname, blend=True, m_repeat=True, automatic_resize=False)
    return tex

def tidy_name(path_name):
    name = os.path.basename(path_name).upper()
    name = ''.join([c for c in name if c in CODEPOINTS])
    return name

def get_files(dt_from=None, dt_to=None):
  # dt_from and dt_to are either None or tuples (2016,12,25)
  if dt_from is not None:
    dt_from = time.mktime(dt_from + (0, 0, 0, 0, 0, 0))
  if dt_to is not None:
    dt_to = time.mktime(dt_to + (0, 0, 0, 0, 0, 0))
  global shuffle, PIC_DIR, EXIF_DATID
  file_list = []
  extensions = ['.png','.jpg','.jpeg'] # can add to these
  for root, _dirnames, filenames in os.walk(PIC_DIR):
      for filename in filenames:
          ext = os.path.splitext(filename)[1].lower()
          if ext in extensions and not '.AppleDouble' in root and not filename.startswith('.'):
              file_path_name = os.path.join(root, filename)
              include_flag = True
              if EXIF_DATID is not None and (dt_from is not None or dt_to is not None):
                try:
                  im = Image.open(file_path_name) # lazy operation so shouldn't load (better test though)
                  dt = time.mktime(
                        time.strptime(im._getexif()[EXIF_DATID], '%Y:%m:%d %H:%M:%S'))
                  if (dt_from is not None and dt < dt_from) or (dt_to is not None and dt > dt_to):
                    include_flag = False
                except: # NB should really check error here but it's almost certainly due to lack of exif data
                  include_flag = True # could use os date info or try parsing file name for testing just reject
              if include_flag:
                file_list.append(file_path_name) 
  if shuffle:
    random.shuffle(file_list) # randomize pictures
  else:
    file_list.sort() # if not suffled; sort by name
  return file_list, len(file_list) # tuple of file list, number of pictures

EXIF_DATID = None # this needs to be set before get_files() above can extract exif date info
for k in ExifTags.TAGS:
  if ExifTags.TAGS[k] == 'DateTime':
    EXIF_DATID = k
    break

##############################################
# MQTT functionality - see http://pi3d.github.io/html/FAQ.html
##############################################
try:
  def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")

  def on_message(client, userdata, message):
    # TODO not ideal to have global but probably only reasonable way to do it
    global pic_num, iFiles, nFi, date_from, date_to, time_delay
    global delta_alpha, fade_time, shuffle, quit
    msg = message.payload.decode("utf-8")
    if message.topic == "frame/date_from": # NB entered as mqtt string "2016:12:25"
      df = msg.split(":")
      date_from = tuple(int(i) for i in df)
    elif message.topic == "frame/date_to":
      df = msg.split(":")
      date_to = tuple(int(i) for i in df)
    elif message.topic == "frame/time_delay":
      time_delay = float(msg)
    elif message.topic == "frame/fade_time":
      fade_time = float(msg)
      delta_alpha = 1.0 / (FPS * fade_time)
    elif message.topic == "frame/shuffle":
      shuffle = True if msg == "True" else False
    elif message.topic == "frame/quit":
      quit = True
    iFiles, nFi = get_files(date_from, date_to)
    pic_num = 0

  # set up MQTT listening
  client = mqtt.Client()
  client.username_pw_set("orhellow", "z6kfIctiONxP") # replace with your own id
  client.connect("postman.cloudmqtt.com", 16845, 60) # replace with your own server
  client.loop_start()
  client.subscribe("frame/date_from", qos=0)
  client.subscribe("frame/date_to", qos=0)
  client.subscribe("frame/time_delay", qos=0)
  client.subscribe("frame/fade_time", qos=0)
  client.subscribe("frame/shuffle", qos=0)
  client.subscribe("frame/quit", qos=0)
  client.on_connect = on_connect
  client.on_message = on_message
except Exception as e:
  print("MQTT not set up because of: {}".format(e))
##############################################

DISPLAY = pi3d.Display.create(x=-1, y=-1, frames_per_second=FPS)
CAMERA = pi3d.Camera(is_3d=False)

shader = pi3d.Shader("shaders/blend_new")
slide = pi3d.Sprite(camera=CAMERA, w=DISPLAY.width, h=DISPLAY.height, z=5.0)
slide.set_shader(shader)

kbd = pi3d.Keyboard()

# images in iFiles list
nexttm = 0.0
iFiles, nFi = get_files(date_from, date_to)
pic_num = 0
sfg = tex_load(iFiles[pic_num])

# PointText and TextBlock
font = pi3d.Font(FONT_FILE, codepoints=CODEPOINTS, grid_size=7, shadow_radius=4.0,
                 shadow=(0,0,0,128))
text = pi3d.PointText(font, CAMERA, max_chars=200, point_size=50)
textblock = pi3d.TextBlock(x=-DISPLAY.width * 0.5 + 50, y=-DISPLAY.height * 0.4,
                           z=0.1, rot=0.0, char_count=199,
                           text_format="{}".format(tidy_name(iFiles[pic_num])), size=0.99, 
                           spacing="F", space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(textblock)

while DISPLAY.loop_running():
  tm = time.time()
  if tm > nexttm: # this must run first iteration of loop
    nexttm = tm + time_delay
    a = 0.0 # alpha - proportion front image to back
    sbg = sfg # swap Textures front to back
    pic_num += 1
    if pic_num >= nFi: 
      random.shuffle(iFiles)
      pic_num = 0
    sfg = tex_load(iFiles[pic_num]) # load new Texture for front
    slide.set_textures([sfg, sbg])
    slide.unif[45:47] = slide.unif[42:44] # transfer front width and height factors to back
    slide.unif[51:53] = slide.unif[48:50] # transfer front width and height offsets
    w_rat = DISPLAY.width / sfg.ix # screen width c.f. image width
    h_rat = DISPLAY.height / sfg.iy # and height
    if w_rat > h_rat: # make it fit width - leave gap left and right
      slide.unif[42] = w_rat / h_rat # width
      slide.unif[43] = 1.0
      slide.unif[48] = (slide.unif[42] - 1.0) * 0.5 # offset
      slide.unif[49] = 0.0
    else: # otherwise fit height - leave gap top and bottom
      slide.unif[42] = 1.0
      slide.unif[43] = h_rat / w_rat # height
      slide.unif[48] = 0.0
      slide.unif[49] = (slide.unif[43] - 1.0) * 0.5 # offset
    # set the file name as the description
    textblock.set_text(text_format="{}".format(tidy_name(iFiles[pic_num])))

  if a < 1.0:
    a += delta_alpha
    slide.unif[44] = a
    # this sets alpha for the TextBlock from 0 to 1 then back to 0
    textblock.colouring.set_colour(alpha=(1.0 - abs(1.0 - 2.0 * a)))

  slide.draw()

  text.regen()
  text.draw()

  k = kbd.read()
  if k != -1:
    nexttm = time.time() - 1.0
  if k==27 or quit: #ESC
    break
  if k==ord('s'): # go back a picture
    pic_num -= 2
    if pic_num < -1:
      pic_num = -1

try:
  client.loop_stop()
except Exception as e:
  print("this was going to fail if previous try failed!")
kbd.close()
DISPLAY.destroy()
