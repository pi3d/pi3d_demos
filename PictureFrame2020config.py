""" This is the config file used by PictureFrame. It allows settings to be changed
on the command line when the program is run, or you can alter the default values
here
"""
import argparse

""" function needed to convert str representation of bool values
"""
def str_to_bool(x):
    if len(x) == 0:
        return True # i.e. just arg will set to true
    return not (x.lower()[0] in ('0', 'f', 'n')) # i.e. 0,False,false,No,n

def str_to_tuple(x):
    return tuple(float(v) for v in x.replace("(","").replace(")","").split(","))

def parse_show_text(txt):
    show_text = 0
    txt = txt.lower()
    if "name" in txt:
        show_text |= 1
    if "date" in txt:
        show_text |= 2
    if "location" in txt:
        show_text |= 4
    return show_text

# NB the reason that absolute paths are used here is because relative ones can lead
#  to abiguity if the program is started automatically on boot.
parse = argparse.ArgumentParser("start running a picture frame")
parse.add_argument("-a", "--blur_amount",   default=12, type=float, help="larger values than 12 will increase processing load quite a bit")
parse.add_argument("-b", "--blur_edges",    default=True, type=str_to_bool, help="use blurred version of image to fill edges - will override FIT = False")
parse.add_argument("-c", "--check_dir_tm",  default=60.0, type=float, help="time in seconds between checking if the image directory has changed")
parse.add_argument("-d", "--verbose",       default=False, type=str_to_bool, help="show try/exception messages")
parse.add_argument("-e", "--edge_alpha",    default=0.5, type=float, help="background colour at edge. 1.0 would show reflection of image")
parse.add_argument("-f", "--fps",           default=20.0, type=float)
parse.add_argument("-g", "--background",    default=(0.2, 0.2, 0.3, 1.0), type=str_to_tuple, help="RGBA to fill edges when fitting")
parse.add_argument("-i", "--no_files_img",  default="/home/pi/pi3d_demos/PictureFrame2020img.jpg", help="image to show if none selected")
parse.add_argument("-j", "--blend_type",    default="blend", choices=["blend", "burn", "bump"], help="type of blend the shader can do")
parse.add_argument("-k", "--keyboard",      default=False, type=str_to_bool, help="set to False when running headless to avoid curses error. True for debugging")
parse.add_argument("-m", "--use_mqtt",      default=False)
parse.add_argument(      "--mqtt_server",   default="localhost")
parse.add_argument(      "--mqtt_port",     default=1883, type=int)
parse.add_argument(      "--mqtt_login",    default="")
parse.add_argument(      "--mqtt_password", default="")
parse.add_argument("-n", "--recent_n",      default=0, type=int, help="when shuffling keep n most recent ones to play before the rest")
parse.add_argument("-o", "--font_file",     default="/home/pi/pi3d_demos/fonts/NotoSans-Regular.ttf")
parse.add_argument("-p", "--pic_dir",       default="/home/pi/Pictures")
parse.add_argument("-q", "--shader",        default="/home/pi/pi3d_demos/shaders/blend_new")
parse.add_argument("-r", "--reshuffle_num", default=1, type=int, help="times through before reshuffling")
parse.add_argument("-s", "--show_text_tm",  default=15.0, type=float, help="time to show text over the image")
parse.add_argument(      "--show_text_fm",  default="%B %d, %Y", help="format to show date over the image")
parse.add_argument(      "--show_text_sz",  default=25, type=int, help="text character size")
parse.add_argument(      "--show_text",     default="location", help="show text, include combination of words: name, date, location")
parse.add_argument(      "--text_width",    default=50, type=int, help="number of character before breaking into new line")
parse.add_argument("-t", "--fit",           default=False, type=str_to_bool, help="shrink to fit screen i.e. don't crop")
parse.add_argument("-u", "--kenburns",      default=False, type=str_to_bool, help="will set FIT->False and BLUR_EDGES->False")
parse.add_argument("-v", "--time_delay",    default=30.0, type=float, help="time between consecutive slide starts - can be changed by MQTT")
parse.add_argument("-w", "--fade_time",     default=4.0, type=float, help="change time during which slides overlap - can be changed by MQTT")
parse.add_argument("-x", "--shuffle",       default=True, type=str_to_bool, help="shuffle on reloading image files - can be changed by MQTT")
parse.add_argument("-y", "--subdirectory",  default="", help="subdir of pic_dir - can be changed by MQTT")
parse.add_argument("-z", "--blur_zoom",     default=1.0, type=float, help="must be >= 1.0 which expands the backgorund to just fill the space around the image")
parse.add_argument(      "--auto_resize",   default=True, type=str_to_bool, help="set this to false if you want to use 4K resolution on Raspberry Pi 4. You should ensure your images are the correct size for the display")
parse.add_argument(      "--delay_exif",    default=True, type=str_to_bool, help="set this to false if there are problems with date filtering - it will take a long time for initial loading if there are many images.")
parse.add_argument(      "--locale",        default="de_DE.UTF-8", help="set the locale")
parse.add_argument(      "--load_geoloc",   default=True, type=str_to_bool, help="load geolocation code")
parse.add_argument(      "--geo_key",       default="pictureframe_says_hello", help="set the Nominatim key - change to something unique to you")
parse.add_argument(      "--zoom",          default=18, type=int, help="Level of adress detail(3=country...18=building): 3,5,8,10,14,16,17,18")
parse.add_argument(      "--geo_path",      default="/home/pi/PictureFrame2020gpsdata.txt", help="set the local file to store data from geopy - ignored if --load_geoloc is not true")
parse.add_argument(      "--display_x",     default=0, type=int, help="offset from left of screen (can be negative)")
parse.add_argument(      "--display_y",     default=0, type=int, help="offset from top of screen (can be negative)")
parse.add_argument(      "--display_w",     default=None, type=int, help="width of display surface (None will use max returned by hardware)")
parse.add_argument(      "--display_h",     default=None, type=int, help="height of display surface")
args = parse.parse_args()
print(args.display_x)

BLEND_OPTIONS = {"blend":0.0, "burn":1.0, "bump":2.0} # that work with the blend_new fragment shader

## set uppercase CONST style variables that can be accessed from PictureFrame
BLUR_AMOUNT = args.blur_amount
BLUR_EDGES = args.blur_edges
CHECK_DIR_TM = args.check_dir_tm
VERBOSE = args.verbose
EDGE_ALPHA = args.edge_alpha
FPS = args.fps
BACKGROUND = args.background
NO_FILES_IMG = args.no_files_img
BLEND_TYPE = BLEND_OPTIONS[args.blend_type]
KEYBOARD = args.keyboard
USE_MQTT = args.use_mqtt
MQTT_SERVER = args.mqtt_server
MQTT_PORT = args.mqtt_port
MQTT_LOGIN = args.mqtt_login
MQTT_PASSWORD = args.mqtt_password
RECENT_N = args.recent_n
FONT_FILE = args.font_file
PIC_DIR = args.pic_dir
SHADER = args.shader
RESHUFFLE_NUM = args.reshuffle_num
SHOW_TEXT_TM = args.show_text_tm
SHOW_TEXT_FM = args.show_text_fm
SHOW_TEXT_SZ = args.show_text_sz
SHOW_TEXT = parse_show_text(args.show_text)
TEXT_WIDTH = args.text_width
FIT = args.fit
KENBURNS = args.kenburns
TIME_DELAY = args.time_delay
FADE_TIME = args.fade_time
SHUFFLE = args.shuffle
SUBDIRECTORY = args.subdirectory
BLUR_ZOOM = args.blur_zoom
AUTO_RESIZE = args.auto_resize
DELAY_EXIF = args.delay_exif
LOCALE = args.locale
LOAD_GEOLOC = args.load_geoloc
GEO_KEY = args.geo_key
GEO_PATH = args.geo_path
ZOOM = args.zoom
DISPLAY_X = args.display_x
DISPLAY_Y = args.display_y
DISPLAY_W = args.display_w
DISPLAY_H = args.display_h


CODEPOINTS = '1234567890AÄÀBCÇDÈÉÊEFGHIÍJKLMNÑOÓÖPQRSTUÚÙÜVWXYZ.:, _-/abcdefghijklmnñopqrstuvwxyzáéèêàçíóúäöüß' # limit to 49 ie 7x7 grid_size
