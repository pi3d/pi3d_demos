""" This is the config file used by PictureFrame. It allows settings to be changed
on the command line when the program is run, or you can alter the default values
here
"""
import argparse
import os
import logging

log = logging.getLogger(__name__)


def str_to_tuple(x):
    return tuple(float(v) for v in x.replace("(", "").replace(")", "").split(","))


def parse_show_text(txt):
    show_text = 0
    txt = txt.lower()
    if "name" in txt:
        show_text |= 1
    if "date" in txt:
        show_text |= 2
    if "location" in txt:
        show_text |= 4
    if "folder" in txt:
        show_text |= 8
    return show_text


def setup_parser():
    parser = argparse.ArgumentParser("start running a picture frame")
    vpo = parser.add_argument_group('visual picture options')
    vpo.add_argument("-a", "--blur_amount", default=12, type=float,
                     help="larger values than 12 will increase processing load quite a bit")
    vpo.add_argument("-b", "--blur_edges", action='store_true',
                     help="use blurred version of image to fill edges - will override FIT = False")
    vpo.add_argument("-e", "--edge_alpha", default=0.5, type=float,
                     help="background colour at edge. 1.0 would show reflection of image")
    vpo.add_argument("-g", "--background", default=(0.2, 0.2, 0.3, 1.0), type=str_to_tuple,
                     help="RGBA to fill edges when fitting")
    vpo.add_argument("-j", "--blend_type", default="blend", choices=["blend", "burn", "bump"],
                     help="type of blend the shader can do")
    vpo.add_argument("-f", "--fit", action='store_true', help="shrink to fit screen i.e. don't crop")
    vpo.add_argument("-v", "--time_delay", default=8.0, type=float, help="time between consecutive slide starts")
    vpo.add_argument("-w", "--fade_time", default=1.0, type=float, help="change time during which slides overlap")
    vpo.add_argument("-z", "--blur_zoom", default=1.0, type=float,
                     help="must be >= 1.0 which expands the background to just fill the space around the image")
    vpo.add_argument("--no_auto_resize", dest='auto_resize', action='store_false',
                     help="Set this if you want to use 4K resolution on Raspberry Pi 4."
                          " You should ensure your images are the correct size for the display")

    vto = parser.add_argument_group('visual text options')
    vto.add_argument("-s", "--show_text_tm", default=6.0, type=float, help="time to show text over the image")
    vto.add_argument("--show_date_fm", default="%b %d, %Y", help="format to show date over the image")
    vto.add_argument("--show_text_sz", default=40, type=int, help="text character size")
    vto.add_argument("--show_text", default="date folder location",
                     help="show text, include combination of words: name, date, location")
    vto.add_argument("--text_width", default=90, type=int, help="number of character before breaking into new line")
    # TODO reimplement
    vto.add_argument("--load_geoloc", action='store_true', help="load geolocation code")
    vto.add_argument("--geo_key", default="picture_frame_hello",
                     help="set the Nominatim key - change to something unique to you")
    vto.add_argument("--geo_path", default="/home/pi/PictureFrame2020gpsdata.txt",
                     help="set the local file to store data from geopy - ignored if --load_geoloc is not true")
    vto.add_argument("--geo_zoom", default=10, type=int,
                     help="Level of address detail(3=country...18=building): 3,5,8,10,14,16,17,18")

    fo = parser.add_argument_group('filter options')
    fo.add_argument("--min_rating", default=None, type=int, help="Minimum rating of displayed pictures")
    fo.add_argument("--max_rating", default=None, type=int, help="Maximum rating of displayed pictures")
    # TODO add filters for date_before and date_after

    pfo = parser.add_argument_group('picture file options')
    pfo.add_argument("-c", "--check_dir_tm", default=60.0, type=float,
                     help="time in seconds between checking if the image directory has changed")
    pfo.add_argument("-r", "--reshuffle_num", default=1, type=int, help="times through before reshuffling")
    pfo.add_argument("-x", "--shuffle", action='store_true', help="shuffle on loading image files")

    mo = parser.add_argument_group('misc options')
    mo.add_argument("-l", "--log_level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                    default='WARNING', help="Set the logging level")
    mo.add_argument("-o", "--font_file", default="fonts/NotoSans-Regular.ttf")
    mo.add_argument("-p", "--pic_dir", default="/home/pi/Pictures")
    mo.add_argument("-q", "--shader", default="shaders/blend_new")
    mo.add_argument("--locale", default="en_US.utf8", help="set the locale")
    mo.add_argument("--fps", default=20.0, type=float)
    mo.add_argument("--display_x", default=0, type=int, help="offset from left of screen (can be negative)")
    mo.add_argument("--display_y", default=0, type=int, help="offset from top of screen (can be negative)")
    mo.add_argument("--display_w", default=None, type=int,
                    help="width of display surface (None will use max returned by hardware)")
    mo.add_argument("--display_h", default=None, type=int, help="height of display surface")
    # TODO reimplement
    mo.add_argument("-k", "--keyboard", action='store_true',
                    help="Enable keyboard interaction. ")
    # TODO possibly reimplement
    # parse.add_argument("-i", "--no_files_img",
    #                    default="/home/pi/pi3d_demos/PictureFrame2020img.jpg",
    #                    help="image to show if none selected")
    # parse.add_argument("-m", "--use_mqtt",      default=True)
    # parse.add_argument(      "--mqtt_server",   default="localhost")
    # parse.add_argument(      "--mqtt_port",     default=1883, type=int)
    # parse.add_argument(      "--mqtt_login",    default="")
    # parse.add_argument(      "--mqtt_password", default="")
    # parse.add_argument(      "--mqtt_id",       default="frame", help="prepended onto all the message strings with a / separator added")
    # parse.add_argument("-y", "--subdirectory",  default="", help="subdir of pic_dir - can be changed by MQTT")

    return parser

# TODO Proper implementation
BLEND_OPTIONS = {"blend": 0.0, "burn": 1.0, "bump": 2.0}  # that work with the blend_new fragment shader


def convert_to_absolute_path(rel_path):
    if os.path.isfile(rel_path):
        return os.path.abspath(rel_path)
    else:
        new_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_path)
        if os.path.isfile(new_path):
            return new_path
    log.error(f'{rel_path} is not a file.')
    return None


class Config:
    def __init__(self, args):
        self.blur_amount = args.blur_amount
        self.blur_edges = args.blur_edges
        self.edge_alpha = args.edge_alpha
        self.background = args.background
        self.blend_type = BLEND_OPTIONS[args.blend_type]
        self.fit = args.fit
        self.time_delay = args.time_delay
        self.fade_time = args.fade_time
        self.blur_zoom = args.blur_zoom
        self.auto_resize = args.auto_resize

        self.show_text_tm = args.show_text_tm
        self.show_date_fm = args.show_date_fm
        self.show_text_sz = args.show_text_sz
        self.show_text = parse_show_text(args.show_text)
        self.text_width = args.text_width
        self.load_geoloc = args.load_geoloc
        self.geo_key = args.geo_key
        self.geo_path = args.geo_path
        self.geo_zoom = args.geo_zoom

        self.min_rating = args.min_rating
        self.max_rating = args.max_rating

        self.check_dir_tm = args.check_dir_tm
        self.reshuffle_num = args.reshuffle_num
        self.shuffle = args.shuffle

        self.log_level = args.log_level
        self.fps = args.fps
        self.font_file = convert_to_absolute_path(args.font_file)
        self.pic_dir = args.pic_dir
        # This is needed because the path to the shader is given without the .fs/.vs extension.
        self.shader = convert_to_absolute_path(args.shader + '.fs')[:-3]
        self.local = args.locale
        self.display_x = args.display_x
        self.display_y = args.display_y
        self.display_w = args.display_w
        self.display_h = args.display_h
        self.keyboard = args.keyboard

        # limit to 121 ie 11x11 grid_size
        self.codepoints = "1234567890AÄÀÆÅÃBCÇDÈÉÊEËFGHIÏÍJKLMNÑOÓÖÔŌØPQRSTUÚÙÜVWXYZ" \
                          "aáàãæåäbcçdeéèêëfghiíïjklmnñoóôōøöpqrsßtuúüvwxyz., _-+*()&/`´'•"
