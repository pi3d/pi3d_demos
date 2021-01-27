#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

''' Simplified slideshow system using ImageSprite and without threading for background
loading of images (so may show delay for v large images).
    Also has a minimal use of PointText and TextBlock system with reduced codepoints
and reduced grid_size to give better resolution for large characters.

USING exif info to rotate images
'''
import os
# Needed to load opengl dlls from current dir in Windows.
if os.name == 'nt':
    os.add_dll_directory(os.path.dirname(os.path.realpath(__file__)))
import time
import random
import math
import pi3d
import locale
import numpy as np
import logging

from pi3d.Texture import MAX_SIZE
from PIL import Image, ImageFilter  # these are needed for getting exif data from images
from PictureFrame2021config import setup_parser, Config
from PictureFrame2021pic import Picture

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger('PictureFrame2021')


# --- Sanitize the specified string by removing any chars not found in codepoints
def sanitize_string(string, codepoints):
    return ''.join([c for c in string if c in codepoints])


def initial_setup(config):
    # noinspection PyBroadException
    try:
        locale.setlocale(locale.LC_TIME, config.local)
    except Exception as e:
        log.warning("error trying to set local to {}".format(config.local), e)

    display = pi3d.Display.create(x=config.display_x, y=config.display_y,
                                  w=config.display_w, h=config.display_h, frames_per_second=config.fps,
                                  display_config=pi3d.DISPLAY_CONFIG_HIDE_CURSOR, background=config.background)
    camera = pi3d.Camera(is_3d=False)

    shader = pi3d.Shader(config.shader)
    slide = pi3d.Sprite(camera=camera, w=display.width, h=display.height, z=5.0)
    slide.set_shader(shader)
    slide.unif[47] = config.edge_alpha
    slide.unif[54] = config.blend_type
    slide.unif[55] = 1.0  # brightness used by shader [18][1]

    keyboard = None
    if config.keyboard:
        keyboard = pi3d.Keyboard()

    grid_size = math.ceil(len(config.codepoints) ** 0.5)
    font = pi3d.Font(config.font_file, codepoints=config.codepoints, grid_size=grid_size)
    text = pi3d.PointText(font, camera, max_chars=200, point_size=config.show_text_sz)
    text_block = pi3d.TextBlock(x=0, y=-display.height // 2 + (config.show_text_sz // 2) + 20,
                                z=0.1, rot=0.0, char_count=199,
                                text_format="{}".format(" "), size=0.99,
                                spacing="F", justify=0.5, space=0.02, colour=(1.0, 1.0, 1.0, 1.0))
    text.add_text_block(text_block)

    bkg_ht = display.height // 4
    text_bkg_array = np.zeros((bkg_ht, 1, 4), dtype=np.uint8)
    text_bkg_array[:, :, 3] = np.linspace(0, 170, bkg_ht).reshape(-1, 1)
    text_bkg_tex = pi3d.Texture(text_bkg_array, blend=True, free_after_load=True)
    text_bkg = pi3d.Plane(w=display.width, h=bkg_ht, y=-display.height // 2 + bkg_ht // 2, z=4.0)
    back_shader = pi3d.Shader("uv_flat")
    text_bkg.set_draw_details(back_shader, [text_bkg_tex])

    return display, camera, slide, keyboard, text_block, text, text_bkg


def read_pictures_from_disk(pic_dir):
    extensions = ['.png', '.jpg', '.jpeg', '.heif', '.heic']  # TODO move this to config
    picture_dir = pic_dir
    picture_list = []
    last_file_change = 0
    for root, _, filenames in os.walk(picture_dir):
        mod_tm = os.stat(root).st_mtime  # time of alteration in a directory
        if mod_tm > last_file_change:
            last_file_change = mod_tm
        picture_list = picture_list + [Picture(os.path.join(root, fn))
                                       for fn in filenames
                                       if os.path.splitext(fn)[1].lower() in extensions]
    return picture_list, last_file_change


FILTER_DATE_BEFORE = 'fdb'
FILTER_DATE_AFTER = 'fda'
FILTER_RATING_BELOW = 'frb'
FILTER_RATING_ABOVE = 'fra'


def pic_nums_to_display(picture_list, filters):
    for i in range(len(picture_list)):
        pic = picture_list[i]
        try:
            if FILTER_DATE_BEFORE in filters and pic.exif_data.orig_date_time < filters[FILTER_DATE_BEFORE]:
                log.debug(f'{pic}\nexcluded because of date.')
                continue
            if FILTER_DATE_AFTER in filters and pic.exif_data.orig_date_time > filters[FILTER_DATE_AFTER]:
                log.debug(f'{pic}\nexcluded because of date.')
                continue
            if FILTER_RATING_BELOW in filters and pic.exif_data.rating < filters[FILTER_RATING_BELOW]:
                log.debug(f'{pic}\nexcluded because of rating.')
                continue
            if FILTER_RATING_ABOVE in filters and pic.exif_data.rating > filters[FILTER_RATING_ABOVE]:
                log.debug(f'{pic}\nexcluded because of rating.')
                continue
            log.debug(f'{pic}\nselected.')
        except Exception:
            log.warning(f'Error in file {pic.path}.', exc_info=True)
            continue
        yield i


def load_pictures(filters, pic_dir, shuffle):
    full_picture_list, last_file_change = read_pictures_from_disk(pic_dir)
    log.info(f'{len(full_picture_list)} pictures loaded.')
    if shuffle:
        random.shuffle(full_picture_list)
    else:
        full_picture_list.sort(key=lambda x: x.path)
    pntd_gen = pic_nums_to_display(full_picture_list, filters)
    return full_picture_list, last_file_change, pntd_gen


def orientate_image(im, orientation):
    if orientation == 2:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 3:
        im = im.transpose(Image.ROTATE_180)  # rotations are clockwise
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
    return im


def convert_heif(file_name):
    try:
        # noinspection PyUnresolvedReferences
        import pyheif

        heif_file = pyheif.read(file_name)
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data,
                                "raw", heif_file.mode, heif_file.stride)
        return image
    except Exception as e:
        log.error("Couldn't convert from heif file. Have you installed pyheif?", e)
        exit(2)


def texture_load(pic_num, picture_list, size, config):
    picture = picture_list[pic_num]
    pic_path = picture.path
    orientation = picture.exif_data.orientation

    try:
        ext = os.path.splitext(pic_path)[1].lower()
        if ext in ('.heif', '.heic'):
            im = convert_heif(pic_path)
        else:
            im = Image.open(pic_path)

        (w, h) = im.size
        max_dimension = MAX_SIZE  # changing MAX_SIZE causes serious crash on linux laptop!
        if not config.auto_resize:  # turned off for 4K display - will cause issues on RPi before v4
            max_dimension = 3840  # TODO check if mipmapping should be turned off with this setting.
        if w > max_dimension:
            im = im.resize((max_dimension, int(h * max_dimension / w)), resample=Image.BICUBIC)
        elif h > max_dimension:
            im = im.resize((int(w * max_dimension / h), max_dimension), resample=Image.BICUBIC)
        if orientation > 1:
            im = orientate_image(im, orientation)
        if config.blur_edges and size is not None:
            wh_rat = (size[0] * im.height) / (size[1] * im.width)
            if abs(wh_rat - 1.0) > 0.01:  # make a blurred background if wh_rat is not exactly 1
                (sc_b, sc_f) = (size[1] / im.height, size[0] / im.width)
                if wh_rat > 1.0:
                    (sc_b, sc_f) = (sc_f, sc_b)  # swap round
                (w, h) = (round(size[0] / sc_b / config.blur_zoom), round(size[1] / sc_b / config.blur_zoom))
                (x, y) = (round(0.5 * (im.width - w)), round(0.5 * (im.height - h)))
                box = (x, y, x + w, y + h)
                blr_sz = (int(x * 512 / size[0]) for x in size)
                im_b = im.resize(size, resample=0, box=box).resize(blr_sz)
                im_b = im_b.filter(ImageFilter.GaussianBlur(config.blur_amount))
                im_b = im_b.resize(size, resample=Image.BICUBIC)
                im_b.putalpha(round(255 * config.edge_alpha))  # to apply the same EDGE_ALPHA as the no blur method.
                im = im.resize((int(x * sc_f) for x in im.size), resample=Image.BICUBIC)
                """resize can use Image.LANCZOS (alias for Image.ANTIALIAS) for resampling
                for better rendering of high-contranst diagonal lines. NB downscaled large
                images are rescaled near the start of this try block if w or h > max_dimension
                so those lines might need changing too.
                """
                im_b.paste(im, box=(round(0.5 * (im_b.width - im.width)),
                                    round(0.5 * (im_b.height - im.height))))
                im = im_b  # have to do this as paste applies in place
        tex = pi3d.Texture(im, blend=True, m_repeat=True, automatic_resize=config.auto_resize,
                           free_after_load=True)
        # tex = pi3d.Texture(im, blend=True, m_repeat=True, automatic_resize=config.AUTO_RESIZE,
        #                    mipmap=config.AUTO_RESIZE, free_after_load=True)
        # poss try this if still some artifacts with full resolution
    except Exception as e:
        log.error(f"Error loading file {pic_path}", e)
        tex = None
    return tex


def load_fg(next_pic_num, full_picture_list, display, slide, config):
    cur_pic_num = next_pic_num
    cur_pic = full_picture_list[cur_pic_num]
    sfg = texture_load(cur_pic_num, full_picture_list, (display.width, display.height), config)
    wh_rat = (display.width * sfg.iy) / (display.height * sfg.ix)
    if (wh_rat > 1.0 and config.fit) or (wh_rat <= 1.0 and not config.fit):
        sz1, sz2, os1, os2 = 42, 43, 48, 49
    else:
        sz1, sz2, os1, os2 = 43, 42, 49, 48
        wh_rat = 1.0 / wh_rat
    slide.unif[sz1] = wh_rat
    slide.unif[sz2] = 1.0
    slide.unif[os1] = (wh_rat - 1.0) * 0.5
    slide.unif[os2] = 0.0

    return sfg, cur_pic, slide


def copy_fg_to_bg(slide, sfg):
    sbg = sfg
    slide.unif[45:47] = slide.unif[42:44]  # transfer front width and height factors to back
    slide.unif[51:53] = slide.unif[48:50]  # transfer front width and height offsets
    return slide, sbg


def load_next_slide(slide, sfg, next_pic_num, full_picture_list, display, config):
    slide, sbg = copy_fg_to_bg(slide, sfg)

    sfg, next_pic, slide = load_fg(next_pic_num, full_picture_list, display, slide, config)

    slide.set_textures([sfg, sbg])
    return slide, sfg, sbg, next_pic


def smooth_alpha(a):
    return a * a * (3.0 - 2.0 * a)


def set_fg_bg_ratio(slide, ratio):
    """
    Set ratio of foreground to background. 0 = only bg, 1 = only fg.
    """
    slide.unif[44] = smooth_alpha(ratio)
    return slide


def prepare_text(textblock, text, text_bkg, cur_pic, display, config):
    string_components = []
    if config.show_text > 0:
        if (config.show_text & 1) == 1:  # name
            string_components.append(sanitize_string(os.path.basename(cur_pic.path), config.codepoints))
        if (config.show_text & 2) == 2:  # date
            string_components.append(cur_pic.exif_data.orig_date_time.strftime(config.show_date_fm))
        # TODO fix geoloc
        # if config.LOAD_GEOLOC and (config.SHOW_TEXT & 4) == 4:  # location
        #    loc_string = sanitize_string(iFiles[pic_num].location.strip())
        #    if loc_string:
        #        string_components.append(loc_string)
        if (config.show_text & 8) == 8:  # folder
            string_components.append(sanitize_string(os.path.basename(os.path.dirname(cur_pic.path)),
                                     config.codepoints))

        final_string = " • ".join(string_components)
        textblock.set_text(text_format=final_string, wrap=config.text_width)

        last_ch = len(final_string)
        adj_y = text.locations[:last_ch, 1].min() + display.height // 2  # y pos of last char rel to bottom of screen
        textblock.set_position(y=(textblock.y - adj_y + config.show_text_sz))

    else:  # could have a NO IMAGES selected and being drawn
        textblock.set_text(text_format=" ")
        textblock.colouring.set_colour(alpha=0.0)
        text_bkg.set_alpha(0.0)
    text.regen()
    return textblock, text, text_bkg


def set_text_alpha(textblock, text, text_bkg, alpha):
    alpha = smooth_alpha(alpha)
    textblock.colouring.set_colour(alpha=alpha)
    text.regen()
    text_bkg.set_alpha(alpha)
    text_bkg.draw()
    text.draw()
    return textblock, text, text_bkg


def check_for_changes(last_file_change, pic_dir):
    update = False
    for root, _, _ in os.walk(pic_dir):
        mod_tm = os.stat(root).st_mtime
        if mod_tm > last_file_change:
            last_file_change = mod_tm
            update = True
    log.debug(f'Checked for updates to picture folder. Result = {update}')
    return update


class LoopControlVars:
    def __init__(self, config):
        self.cur_time = time.time()
        self.next_pic_time = self.cur_time + config.time_delay
        self.text_start_time = self.cur_time
        self.folder_recheck_time = self.cur_time + config.check_dir_tm
        # Initially pretend a transition has begun
        self.fg_alpha = 0
        self.text_alpha = 0
        self.transition_running = True
        self.last_file_change = 0

        # TODO Add __str__ and display with general exception catch for easier debugging


def main():
    parser = setup_parser()
    args = parser.parse_args()
    config = Config(args)

    log.setLevel(config.log_level)

    # TODO Moved all boundary checks into argparse config
    if config.blur_zoom < 1.0:
        config.blur_zoom = 1.0
    # TODO move delta_alpha into Config class
    delta_alpha = 1.0 / (config.fps * config.fade_time)

    display, camera, slide, keyboard, text_block, text, text_bkg = initial_setup(config)

    filters = dict()
    if config.min_rating:
        filters[FILTER_RATING_BELOW] = config.min_rating
    if config.max_rating:
        filters[FILTER_RATING_ABOVE] = config.max_rating

    # Set values for first slide a part of ctor
    lcv = LoopControlVars(config)

    full_picture_list, lcv.last_file_change, pntd_gen = load_pictures(filters, config.pic_dir, config.shuffle)

    try:
        next_pic_num = next(pntd_gen)
    except StopIteration as si:
        log.exception("No pictures found to display", si)
        exit(1)

    # Load first picture into fg
    # noinspection PyUnboundLocalVariable
    sfg, cur_pic, slide = load_fg(next_pic_num, full_picture_list, display, slide, config)
    # Immediately copy it to bg
    slide, sbg = copy_fg_to_bg(slide, sfg)
    slide = set_fg_bg_ratio(slide, lcv.fg_alpha)
    slide.set_textures([sfg, sbg])
    text_block, text, text_bkg = prepare_text(text_block, text, text_bkg, cur_pic, display, config)

    num_run_through = 0
    # TODO implement pause functionality
    while display.loop_running():
        lcv.cur_time = time.time()
        if lcv.cur_time > lcv.next_pic_time and not lcv.transition_running:
            log.debug('Starting transition')
            lcv.text_start_time = lcv.cur_time
            lcv.next_pic_time = lcv.next_pic_time + config.time_delay
            # noinspection PyUnboundLocalVariable
            text_block, text, text_bkg = prepare_text(text_block, text, text_bkg, next_pic, display, config)
            lcv.transition_running = True

        if lcv.transition_running:
            lcv.fg_alpha += delta_alpha
            lcv.text_alpha = lcv.fg_alpha
            if lcv.fg_alpha > 1.0:
                log.debug('Transition finished')
                # When the transition ends copy the slide shown to bg and load the next slide into fg
                lcv.transition_running = False
                try:
                    next_pic_num = next(pntd_gen)
                except StopIteration:  # Iterated through all pictures
                    num_run_through += 1
                    log.info(f'Finished showing all pictures {num_run_through} times.')
                    if config.shuffle and num_run_through % config.reshuffle_num == 0:
                        log.info('Reshuffling picture list.')
                        random.shuffle(full_picture_list)
                    pntd_gen = pic_nums_to_display(full_picture_list, filters)
                    next_pic_num = next(pntd_gen)
                slide, sfg, sbg, next_pic = load_next_slide(slide, sfg, next_pic_num,
                                                            full_picture_list, display, config)
                lcv.fg_alpha = 0
            slide = set_fg_bg_ratio(slide, lcv.fg_alpha)

        slide.draw()

        # Text shouldn't be shown anymore, min is needed if show text time is longer than time delay
        if lcv.cur_time > lcv.text_start_time + min(config.show_text_tm, config.time_delay - 1):
            if lcv.text_alpha > 0:
                lcv.text_alpha -= delta_alpha
            else:
                lcv.text_alpha = 0
            text_block, text, text_bkg = set_text_alpha(text_block, text, text_bkg, lcv.text_alpha)
        elif lcv.transition_running:
            text_block, text, text_bkg = set_text_alpha(text_block, text, text_bkg, lcv.text_alpha)
        else:
            text_block, text, text_bkg = set_text_alpha(text_block, text, text_bkg, 1)

        # Also check that now transition is running to avoid artefacts:
        if lcv.cur_time > lcv.folder_recheck_time and lcv.fg_alpha == 0 and lcv.text_alpha == 0:
            lcv.folder_recheck_time = lcv.cur_time + config.check_dir_tm
            if check_for_changes(lcv.last_file_change, config.pic_dir):
                log.info('Changes detected in picture folder. Reloading full picture list.')
                full_picture_list, lcv.last_file_change, pntd_gen =\
                    load_pictures(filters, config.pic_dir, config.shuffle)

        if config.keyboard:
            k = keyboard.read()
            if k != -1:
                lcv.transition_running = True
            if k == 27:  # ESC
                break
            if k == ord(' '):
                pass
                # paused = not paused

    if config.keyboard:
        keyboard.close()
    display.destroy()


if __name__ == "__main__":
    main()
