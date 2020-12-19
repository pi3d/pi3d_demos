#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' Simplified slideshow system using ImageSprite and without threading for background
loading of images (so may show delay for v large images).
    Also has a minimal use of PointText and TextBlock system with reduced  codepoints
and reduced grid_size to give better resolution for large characters.
    Also shows a simple use of MQTT to control the slideshow parameters remotely
see http://pi3d.github.io/html/FAQ.html and https://www.thedigitalpictureframe.com/control-your-digital-picture-frame-with-home-assistents-wifi-presence-detection-and-mqtt/
and https://www.cloudmqtt.com/plans.html

USING exif info to rotate images

    ESC to quit, 's' to reverse, any other key to move on one.
'''
import os
import time
import random
import math
import demo
import pi3d
import locale
import subprocess

from pi3d.Texture import MAX_SIZE
from PIL import Image, ExifTags, ImageFilter # these are needed for getting exif data from images
import PictureFrame2020config as config

try:
  locale.setlocale(locale.LC_TIME, config.LOCALE)
except:
  print("error trying to set local to {}".format(config.LOCALE))

#####################################################
# these variables can be altered using MQTT messaging
#####################################################
time_delay = config.TIME_DELAY
fade_time = config.FADE_TIME
shuffle = config.SHUFFLE
subdirectory = config.SUBDIRECTORY
date_from = None
date_to = None
quit = False
paused = False # NB must be set to True *only* after the first iteration of the show!
#####################################################
# only alter below here if you're keen to experiment!
#####################################################
if config.KENBURNS:
  kb_up = True
  config.FIT = False
  config.BLUR_EDGES = False
if config.BLUR_ZOOM < 1.0:
  config.BLUR_ZOOM = 1.0
delta_alpha = 1.0 / (config.FPS * fade_time) # delta alpha
last_file_change = 0.0 # holds last change time in directory structure
next_check_tm = time.time() + config.CHECK_DIR_TM # check if new file or directory every n seconds
#####################################################
# some functions to tidy subsequent code
#####################################################
def tex_load(pic_num, iFiles, size=None):
  global date_from, date_to
  if type(pic_num) is int:
    fname = iFiles[pic_num][0]
    orientation = iFiles[pic_num][1]
  else: # allow file name to be passed to this function ie for missing file image
    fname = pic_num
    orientation = 1
  try:
    ext = os.path.splitext(fname)[1].lower()
    if ext in ('.heif','.heic'):
      im = convert_heif(fname)
    else:
      im = Image.open(fname)
    if config.DELAY_EXIF and type(pic_num) is int: # don't do this if passed a file name
      if iFiles[pic_num][3] is None or iFiles[pic_num][4] is None: # dt and fdt set to None before exif read
        (orientation, dt, fdt, location) = get_exif_info(fname, im)
        iFiles[pic_num][1] = orientation
        iFiles[pic_num][3] = dt
        iFiles[pic_num][4] = fdt
        iFiles[pic_num][5] = location
      if date_from is not None:
        if dt < time.mktime(date_from + (0, 0, 0, 0, 0, 0)):
          return None
      if date_to is not None:
        if dt > time.mktime(date_to + (0, 0, 0, 0, 0, 0)):
          return None
    (w, h) = im.size
    max_dimension = MAX_SIZE # TODO changing MAX_SIZE causes serious crash on linux laptop!
    if not config.AUTO_RESIZE: # turned off for 4K display - will cause issues on RPi before v4
        max_dimension = 3840 # TODO check if mipmapping should be turned off with this setting.
    if w > max_dimension:
        im = im.resize((max_dimension, int(h * max_dimension / w)), resample=Image.BICUBIC)
    elif h > max_dimension:
        im = im.resize((int(w * max_dimension / h), max_dimension), resample=Image.BICUBIC)
    if orientation == 2:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 3:
        im = im.transpose(Image.ROTATE_180) # rotations are clockwise
    elif orientation == 4:
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
    elif orientation == 5:
        im = im.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
    elif orientation == 6:
        im = im.transpose(Image.ROTATE_270)
    elif orientation == 7:
        im = im.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
    elif orientation == 8:
        im = im.transpose(Image.ROTATE_90)
    if config.BLUR_EDGES and size is not None:
      wh_rat = (size[0] * im.size[1]) / (size[1] * im.size[0])
      if abs(wh_rat - 1.0) > 0.01: # make a blurred background
        (sc_b, sc_f) = (size[1] / im.size[1], size[0] / im.size[0])
        if wh_rat > 1.0:
          (sc_b, sc_f) = (sc_f, sc_b) # swap round
        (w, h) =  (round(size[0] / sc_b / config.BLUR_ZOOM), round(size[1] / sc_b / config.BLUR_ZOOM))
        (x, y) = (round(0.5 * (im.size[0] - w)), round(0.5 * (im.size[1] - h)))
        box = (x, y, x + w, y + h)
        blr_sz = (int(x * 512 / size[0]) for x in size)
        im_b = im.resize(size, resample=0, box=box).resize(blr_sz)
        im_b = im_b.filter(ImageFilter.GaussianBlur(config.BLUR_AMOUNT))
        im_b = im_b.resize(size, resample=Image.BICUBIC)
        im_b.putalpha(round(255 * config.EDGE_ALPHA))  # to apply the same EDGE_ALPHA as the no blur method.
        im = im.resize((int(x * sc_f) for x in im.size), resample=Image.BICUBIC)
        """resize can use Image.LANCZOS (alias for Image.ANTIALIAS) for resampling
        for better rendering of high-contranst diagonal lines. NB downscaled large
        images are rescaled near the start of this try block if w or h > max_dimension
        so those lines might need changing too.
        """
        im_b.paste(im, box=(round(0.5 * (im_b.size[0] - im.size[0])),
                            round(0.5 * (im_b.size[1] - im.size[1]))))
        im = im_b # have to do this as paste applies in place
    tex = pi3d.Texture(im, blend=True, m_repeat=True, automatic_resize=config.AUTO_RESIZE,
                        free_after_load=True)
    #tex = pi3d.Texture(im, blend=True, m_repeat=True, automatic_resize=config.AUTO_RESIZE,
    #                    mipmap=config.AUTO_RESIZE, free_after_load=True) # poss try this if still some artifacts with full resolution
  except Exception as e:
    if config.VERBOSE:
        print('''Couldn't load file {} giving error: {}'''.format(fname, e))
    tex = None
  return tex

def tidy_name(path_name):
    name = os.path.basename(path_name)
    name = ''.join([c for c in name if c in config.CODEPOINTS])
    return name

def check_changes():
  global last_file_change
  update = False
  for root, _, _ in os.walk(config.PIC_DIR):
      mod_tm = os.stat(root).st_mtime
      if mod_tm > last_file_change:
        last_file_change = mod_tm
        update = True
  return update

def get_files(dt_from=None, dt_to=None):
  # dt_from and dt_to are either None or tuples (2016,12,25)
  if dt_from is not None:
    dt_from = time.mktime(dt_from + (0, 0, 0, 0, 0, 0))
  if dt_to is not None:
    dt_to = time.mktime(dt_to + (0, 0, 0, 0, 0, 0))
  global shuffle, EXIF_DATID, last_file_change
  file_list = []
  extensions = ['.png','.jpg','.jpeg','.heif','.heic'] # can add to these
  picture_dir = os.path.join(config.PIC_DIR, subdirectory)
  for root, _dirnames, filenames in os.walk(picture_dir):
      mod_tm = os.stat(root).st_mtime # time of alteration in a directory
      if mod_tm > last_file_change:
        last_file_change = mod_tm
      for filename in filenames:
          ext = os.path.splitext(filename)[1].lower()
          if ext in extensions and not '.AppleDouble' in root and not filename.startswith('.'):
              file_path_name = os.path.join(root, filename)
              include_flag = True
              orientation = 1 # this is default - unrotated
              dt = None # if exif data not read - used for checking in tex_load
              fdt = None
              location = ""
              if not config.DELAY_EXIF and EXIF_DATID is not None and EXIF_ORIENTATION is not None:
                (orientation, dt, fdt, location) = get_exif_info(file_path_name)
                if (dt_from is not None and dt < dt_from) or (dt_to is not None and dt > dt_to):
                  include_flag = False
              if include_flag:
                # iFiles now list of lists [file_name, orientation, file_changed_date, exif_date, exif_formatted_date]
                file_list.append([file_path_name,
                                  orientation,
                                  os.path.getmtime(file_path_name),
                                  dt,
                                  fdt,
                                  location])
  if shuffle:
    file_list.sort(key=lambda x: x[2]) # will be later files last
    temp_list_first = file_list[-config.RECENT_N:]
    temp_list_last = file_list[:-config.RECENT_N]
    random.seed()
    random.shuffle(temp_list_first)
    random.shuffle(temp_list_last)
    file_list = temp_list_first + temp_list_last
  else:
    file_list.sort() # if not suffled; sort by name
  return file_list, len(file_list) # tuple of file list, number of pictures

def get_exif_info(file_path_name, im=None):
  dt = os.path.getmtime(file_path_name) # so use file last modified date
  orientation = 1
  location = ""
  try:
    if im is None:
      im = Image.open(file_path_name) # lazy operation so shouldn't load (better test though)
    exif_data = im._getexif() # TODO check if/when this becomes proper function
    if EXIF_DATID in exif_data:
        exif_dt = time.strptime(exif_data[EXIF_DATID], '%Y:%m:%d %H:%M:%S')
        dt = time.mktime(exif_dt)
    if EXIF_ORIENTATION in exif_data:
        orientation = int(exif_data[EXIF_ORIENTATION])
    if config.LOAD_GEOLOC and geo.EXIF_GPSINFO in exif_data:
      location = geo.get_location(exif_data[geo.EXIF_GPSINFO])
  except Exception as e: # NB should really check error here but it's almost certainly due to lack of exif data
    if config.VERBOSE:
      print('trying to read exif', e)
  fdt = time.strftime(config.SHOW_TEXT_FM, time.localtime(dt))
  return (orientation, dt, fdt, location)

def convert_heif(fname):
    try:
        import pyheif
        from PIL import Image

        heif_file = pyheif.read(fname)
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data,
                                "raw", heif_file.mode, heif_file.stride)
        return image
    except:
        print("have you installed pyheif?")

EXIF_DATID = None # this needs to be set before get_files() above can extract exif date info
EXIF_ORIENTATION = None
for k in ExifTags.TAGS:
  if ExifTags.TAGS[k] == 'DateTimeOriginal':
    EXIF_DATID = k
  if ExifTags.TAGS[k] == 'Orientation':
    EXIF_ORIENTATION = k

if config.LOAD_GEOLOC:
  import PictureFrame2020geo as geo

##############################################
# MQTT functionality - see https://www.thedigitalpictureframe.com/
##############################################
iFiles = []
nFi = 0
next_pic_num = 0
if config.USE_MQTT:
  try:
    import paho.mqtt.client as mqtt
    def on_connect(client, userdata, flags, rc):
      if config.VERBOSE:
        print("Connected to MQTT broker")

    def on_message(client, userdata, message):
      # TODO not ideal to have global but probably only reasonable way to do it
      global next_pic_num, iFiles, nFi, date_from, date_to, time_delay
      global delta_alpha, fade_time, shuffle, quit, paused, nexttm, subdirectory
      TRUTH_VALS = {"on":True, "off":False, "true":True, "false":False, "yes":True, "no":False}
      msg = message.payload.decode("utf-8")
      try:
        float_msg = float(msg)
      except:
        float_msg = 0.0
      reselect = False
      refresh = False
      if message.topic == "frame/date_from": # NB entered as mqtt string "2016:12:25"
        try:
          msg = msg.replace(".",":").replace("/",":").replace("-",":")
          df = msg.split(":")
          date_from = tuple(int(i) for i in df)
          if len(date_from) != 3:
            raise Exception("invalid date format")
        except:
          date_from = None
        reselect = True
      elif message.topic == "frame/date_to":
        try:
          msg = msg.replace(".",":").replace("/",":").replace("-",":")
          df = msg.split(":")
          date_to = tuple(int(i) for i in df)
          if len(date_to) != 3:
            raise Exception("invalid date format")
        except:
          date_from = None
        reselect = True
      elif message.topic == "frame/time_delay":
        if float_msg > 0.0:
          time_delay = float_msg
      elif message.topic == "frame/fade_time":
        if float_msg > 0.0:
          fade_time = float_msg
        delta_alpha = 1.0 / (config.FPS * fade_time)
      elif message.topic == "frame/shuffle":
        msg_val = msg.lower()
        shuffle = TRUTH_VALS[msg_val] if msg_val in TRUTH_VALS else False
        reselect = True
      elif message.topic == "frame/quit":
        quit = True
      elif message.topic == "frame/paused":
        msg_val = msg.lower()
        #paused_vals = {"on":True, "off":False, "true":True, "false":False, "yes":True, "no":False}
        paused = TRUTH_VALS[msg_val] if msg_val in TRUTH_VALS else not paused # toggle from previous value
        next_pic_num -= 1
        refresh = True
      elif message.topic == "frame/back":
        next_pic_num -= 2
        refresh = True
      elif message.topic == "frame/next":
        refresh = True
      elif message.topic == "frame/subdirectory":
        subdirectory = msg
        reselect = True
      elif message.topic == "frame/delete":
        f_to_delete = iFiles[pic_num][0]
        f_name_to_delete = os.path.split(f_to_delete)[1]
        move_to_dir = os.path.expanduser("/home/pi/DeletedPictures")
        if not os.path.exists(move_to_dir):
          #os.makedirs(move_to_dir) # creates directory owned by root if picture frame run with sudo so...
          os.system("sudo -u pi mkdir {}".format(move_to_dir))
        os.rename(f_to_delete, os.path.join(move_to_dir, f_name_to_delete))
        iFiles.pop(pic_num)
        nFi -= 1
        refresh = True
      elif message.topic == "frame/text_on":
          config.SHOW_TEXT_TM = float_msg if float_msg > 2.0 else 0.33 * config.TIME_DELAY
          config.SHOW_TEXT ^= 1
          next_pic_num -= 1
          refresh = True
      elif message.topic == "frame/date_on":
          config.SHOW_TEXT_TM = float_msg if float_msg > 2.0 else 0.33 * config.TIME_DELAY
          config.SHOW_TEXT ^= 2
          next_pic_num -= 1
          refresh = True
      elif message.topic == "frame/location_on":
          config.SHOW_TEXT_TM = float_msg if float_msg > 2.0 else 0.33 * config.TIME_DELAY
          config.SHOW_TEXT ^= 4
          next_pic_num -= 1
          refresh = True
      elif message.topic == "frame/text_off":
          config.SHOW_TEXT = 0
          next_pic_num -= 1
          refresh = True
      elif message.topic == "frame/text_refresh":
          next_pic_num -= 1
          refresh = True

      if reselect:
        iFiles, nFi = get_files(date_from, date_to)
        next_pic_num = 0
      if refresh:
        if next_pic_num < -1:
          next_pic_num = -1
        nexttm = time.time() - 86400.0


    # set up MQTT listening
    client = mqtt.Client()
    client.username_pw_set(config.MQTT_LOGIN, config.MQTT_PASSWORD)
    client.connect(config.MQTT_SERVER, config.MQTT_PORT, 60)
    client.loop_start()
    client.subscribe("frame/date_from", qos=0) # needs payload as 2019:06:01 or divided by ":", "/", "-" or "."
    client.subscribe("frame/date_to", qos=0)
    client.subscribe("frame/time_delay", qos=0) # payload seconds for each slide
    client.subscribe("frame/fade_time", qos=0) # payload seconds for fade time between slides
    client.subscribe("frame/shuffle", qos=0) # payload on, yes, true (not case sensitive) will set shuffle on and reshuffle
    client.subscribe("frame/quit", qos=0)
    client.subscribe("frame/paused", qos=0) # payload on, yes, true pause, off, no, false un-pause. Anything toggle state
    client.subscribe("frame/back", qos=0)
    client.subscribe("frame/next", qos=0)
    client.subscribe("frame/subdirectory", qos=0) # payload string must match a subdirectory of pic_dir
    client.subscribe("frame/delete", qos=0) # delete current image, copy to dir set in config
    client.subscribe("frame/text_on", qos=0) # toggle file name on and off. payload text show time in seconds
    client.subscribe("frame/date_on", qos=0) # toggle date (exif if avail else file) on and off. payload show time
    client.subscribe("frame/location_on", qos=0) # toggle location (if enabled) on and off. payload show time
    client.subscribe("frame/text_off", qos=0) # turn all name, date, location off
    client.subscribe("frame/text_refresh", qos=0) # restarts current slide showing text set above
    client.on_connect = on_connect
    client.on_message = on_message
    client.publish("frame/paused", payload="off", qos=0) # un-pause the slideshow on start
  except Exception as e:
    if config.VERBOSE:
      print("MQTT not set up because of: {}".format(e)) # sometimes starts paused
##############################################

DISPLAY = pi3d.Display.create(x=config.DISPLAY_X, y=config.DISPLAY_Y,
              w=config.DISPLAY_W, h=config.DISPLAY_H, frames_per_second=config.FPS,
              display_config=pi3d.DISPLAY_CONFIG_HIDE_CURSOR, background=config.BACKGROUND)
CAMERA = pi3d.Camera(is_3d=False)

shader = pi3d.Shader(config.SHADER)
slide = pi3d.Sprite(camera=CAMERA, w=DISPLAY.width, h=DISPLAY.height, z=5.0)
slide.set_shader(shader)
slide.unif[47] = config.EDGE_ALPHA
slide.unif[54] = config.BLEND_TYPE

if config.KEYBOARD:
  kbd = pi3d.Keyboard()

# images in iFiles list
nexttm = 0.0
iFiles, nFi = get_files(date_from, date_to)
next_pic_num = 0
sfg = None # slide for background
sbg = None # slide for foreground

# PointText and TextBlock. If SHOW_TEXT_TM <= 0 then this is just used for no images message
grid_size = math.ceil(len(config.CODEPOINTS) ** 0.5)
font = pi3d.Font(config.FONT_FILE, codepoints=config.CODEPOINTS, grid_size=grid_size)
text = pi3d.PointText(font, CAMERA, max_chars=200, point_size=config.SHOW_TEXT_SZ)
textblock = pi3d.TextBlock(x=-DISPLAY.width * 0.5 + 50, y=-DISPLAY.height * 0.4,
                          z=0.1, rot=0.0, char_count=199,
                          text_format="{}".format(" "), size=0.99,
                          spacing="F", space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
text.add_text_block(textblock)
back_shader = pi3d.Shader("mat_flat")
text_bkg = pi3d.Sprite(w=DISPLAY.width, h=90, y=-DISPLAY.height * 0.4 - 20, z=4.0)
text_bkg.set_shader(back_shader)
text_bkg.set_material((0, 0, 0))


num_run_through = 0
while DISPLAY.loop_running():
  tm = time.time()
  if (tm > nexttm and not paused) or (tm - nexttm) >= 86400.0: # this must run first iteration of loop
    if nFi > 0:
      nexttm = tm + time_delay
      sbg = sfg
      sfg = None
      start_pic_num = next_pic_num
      loop_count = 0
      while sfg is None: # keep going through until a usable picture is found
        pic_num = next_pic_num
        sfg = tex_load(pic_num, iFiles, (DISPLAY.width, DISPLAY.height))
        next_pic_num += 1
        if next_pic_num >= nFi:
          num_run_through += 1
          if shuffle and num_run_through >= config.RESHUFFLE_NUM:
            num_run_through = 0
            random.shuffle(iFiles)
          next_pic_num = 0
        loop_count += 1
        if loop_count > nFi: #i.e. no images found where tex_load doesn't return None
          nFi = 0
          break
      # set the file name as the description
      if config.SHOW_TEXT > 0 or paused: #was SHOW_TEXT_TM > 0.0
        txt = ""
        gap = ""
        if (config.SHOW_TEXT & 1) == 1: # name
          txt += "{}".format(tidy_name(iFiles[pic_num][0]))
          gap = " "
        if (config.SHOW_TEXT & 2) == 2: # date
          txt += "{}{}".format(gap, iFiles[pic_num][4])
          gap = " "
        if config.LOAD_GEOLOC and (config.SHOW_TEXT & 4) == 4: # location
          txt += "{}{}".format(gap, iFiles[pic_num][5])
        if paused:
          txt += " PAUSED"
        textblock.set_text(text_format=txt, wrap=config.TEXT_WIDTH)
      else: # could have a NO IMAGES selected and being drawn
        textblock.set_text(text_format="{}".format(" "))
        textblock.colouring.set_colour(alpha=0.0)
        text_bkg.set_alpha(0.0)
      text.regen()
    if sfg is None:
      sfg = tex_load(config.NO_FILES_IMG, 1, (DISPLAY.width, DISPLAY.height))
      if sfg is None:
          print("NO FILES image not loaded, check path!")
          break
      sbg = sfg

    a = 0.0 # alpha - proportion front image to back
    text_tm = tm + config.SHOW_TEXT_TM
    if sbg is None: # first time through
      sbg = sfg
    slide.set_textures([sfg, sbg])
    slide.unif[45:47] = slide.unif[42:44] # transfer front width and height factors to back
    slide.unif[51:53] = slide.unif[48:50] # transfer front width and height offsets
    wh_rat = (DISPLAY.width * sfg.iy) / (DISPLAY.height * sfg.ix)
    if (wh_rat > 1.0 and config.FIT) or (wh_rat <= 1.0 and not config.FIT):
      sz1, sz2, os1, os2 = 42, 43, 48, 49
    else:
      sz1, sz2, os1, os2 = 43, 42, 49, 48
      wh_rat = 1.0 / wh_rat
    slide.unif[sz1] = wh_rat
    slide.unif[sz2] = 1.0
    slide.unif[os1] = (wh_rat - 1.0) * 0.5
    slide.unif[os2] = 0.0
    if config.KENBURNS:
        xstep, ystep = (slide.unif[i] * 2.0 / time_delay for i in (48, 49))
        slide.unif[48] = 0.0
        slide.unif[49] = 0.0
        kb_up = not kb_up

  if config.KENBURNS:
    t_factor = nexttm - tm
    if kb_up:
      t_factor = time_delay - t_factor
    slide.unif[48] = xstep * t_factor
    slide.unif[49] = ystep * t_factor

  if a < 1.0: # transition is happening
    a += delta_alpha
    if a > 1.0:
      a = 1.0
    slide.unif[44] = a * a * (3.0 - 2.0 * a)
  else: # no transition effect safe to resuffle etc
    if tm > next_check_tm:
      if check_changes():
        iFiles, nFi = get_files(date_from, date_to)
        num_run_through = 0
        next_pic_num = 0
      next_check_tm = tm + config.CHECK_DIR_TM # once per hour

  slide.draw()

  if nFi <= 0:
    textblock.set_text("NO IMAGES SELECTED")
    textblock.colouring.set_colour(alpha=1.0)
    next_tm = tm + 1.0
    text.regen()
  elif tm < text_tm and (config.SHOW_TEXT > 0 or paused):#config.SHOW_TEXT_TM > 0.0:
    # this sets alpha for the TextBlock from 0 to 1 then back to 0
    dt = (config.SHOW_TEXT_TM - text_tm + tm + 0.1) / config.SHOW_TEXT_TM
    ramp_pt = max(4.0, config.SHOW_TEXT_TM / 4.0)
    alpha = max(0.0, min(1.0, ramp_pt * (a - abs(1.0 - 2.0 * dt)))) # cap text alpha at image alpha
    textblock.colouring.set_colour(alpha=alpha)
    text.regen()
    text_bkg.set_alpha(alpha * 0.6)
    if len(textblock.text_format.strip()) > 0: #only draw background if text there
      text_bkg.draw()

  text.draw()

  if config.KEYBOARD:
    k = kbd.read()
    if k != -1:
      nexttm = time.time() - 86400.0
    if k==27: #ESC
      break
    if k==ord(' '):
      paused = not paused
    if k==ord('s'): # go back a picture
      next_pic_num -= 2
      if next_pic_num < -1:
        next_pic_num = -1
  if quit: # set by MQTT
    break

try:
  client.loop_stop()
except Exception as e:
  if config.VERBOSE:
    print("this was going to fail if previous try failed!")
if config.KEYBOARD:
  kbd.close()
DISPLAY.destroy()