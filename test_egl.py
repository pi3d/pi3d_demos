""" debugging on windows computer """
from pi3d.constants.egl import *
from pi3d.constants.gl import *
from pi3d.constants.gl2 import *
from pi3d.constants.gl2ext import *
from pi3d.util.Ctypes import c_ints
import ctypes
from ctypes import c_int, c_float
import pygame
import os, fnmatch

EGL_DEFAULT_DISPLAY = 0
EGL_NO_CONTEXT = 0
EGL_NO_DISPLAY = 0
EGL_NO_SURFACE = 0
EGL_FALSE = 0
EGL_TRUE = 1

EGL_PLATFORM_ANGLE_ANGLE = 0x3202
EGL_PLATFORM_ANGLE_TYPE_ANGLE = 0x3203
EGL_PLATFORM_ANGLE_MAX_VERSION_MAJOR_ANGLE = 0x3204 
EGL_PLATFORM_ANGLE_MAX_VERSION_MINOR_ANGLE = 0x3205 
EGL_PLATFORM_ANGLE_TYPE_DEFAULT_ANGLE = 0x3206 
EGL_PLATFORM_ANGLE_TYPE_D3D9_ANGLE = 0x3207 
EGL_PLATFORM_ANGLE_TYPE_D3D11_ANGLE = 0x3208 
EGL_PLATFORM_ANGLE_DEVICE_TYPE_ANGLE = 0x3209 
EGL_PLATFORM_ANGLE_DEVICE_TYPE_HARDWARE_ANGLE = 0x320A 
EGL_PLATFORM_ANGLE_DEVICE_TYPE_WARP_ANGLE = 0x320B 
EGL_ANGLE_DISPLAY_ALLOW_RENDER_TO_BACK_BUFFER = 0x320B
EGL_PLATFORM_ANGLE_DEVICE_TYPE_REFERENCE_ANGLE = 0x320C 
EGL_PLATFORM_ANGLE_ENABLE_AUTOMATIC_TRIM_ANGLE = 0x320F

pygame.init()
d = pygame.display.set_mode((0, 0), pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.OPENGL)
info = pygame.display.Info()
width, height = info.current_w, info.current_h

egl_attr = {"EGL_RED_SIZE": EGL_RED_SIZE, "EGL_GREEN_SIZE": EGL_GREEN_SIZE,
           "EGL_BLUE_SIZE": EGL_BLUE_SIZE, "EGL_DEPTH_SIZE": EGL_DEPTH_SIZE,
           "EGL_ALPHA_SIZE": EGL_ALPHA_SIZE, "EGL_BUFFER_SIZE": EGL_BUFFER_SIZE,
           "EGL_SAMPLES": EGL_SAMPLES, "EGL_SURFACE_TYPE": EGL_SURFACE_TYPE}

print("""For ref\n  EGL_FALSE=0x{:04X}\n  EGL_BAD_DISPLAY=0x{:04X}\n  EGL_BAD_ATTRIBUTE=0x{:04X}
  EGL_NOT_INITIALIZED=0x{:04X}\n  EGL_BAD_PARAMETER=0x{:04X}\n  EGL_WINDOW_BIT=0x{:04X}\n""".format(
  EGL_FALSE, EGL_BAD_DISPLAY, EGL_BAD_ATTRIBUTE, EGL_NOT_INITIALIZED, 
  EGL_BAD_PARAMETER, EGL_WINDOW_BIT))

########################################################################
# change to match locations on your computer where you've found libegl.dll

#path = "C:/Program Files (x86)/Google/Chrome/Application/42.0.2311.152"
#path = "C:\\Program Files (x86)\\Google\Chrome\\Application\\42.0.2311.135"
path = ""
""" NB this last 'same diretory' path is to check with the dll files that
have to be in the same directory as this python script (test_egl.py) i.e.
the ones I compiled (download from http://www.eldwick.org.uk/files/libEGL.zip)
or the Mozilla Firefox ones. For these latter you also need to copy over
mozglue.dll
"""
d3dcompiler = ctypes.WinDLL(os.path.join(path, "d3dcompiler_47.dll"))
opengles = ctypes.WinDLL(os.path.join(path, "libglesv2.dll"))
openegl = ctypes.WinDLL(os.path.join(path, "libegl.dll"))

attribute_lists = [c_ints((EGL_PLATFORM_ANGLE_TYPE_ANGLE, EGL_PLATFORM_ANGLE_TYPE_D3D11_ANGLE,
                        EGL_ANGLE_DISPLAY_ALLOW_RENDER_TO_BACK_BUFFER, EGL_TRUE,
                        EGL_PLATFORM_ANGLE_ENABLE_AUTOMATIC_TRIM_ANGLE, EGL_TRUE,
                        EGL_NONE)),
                  c_ints((EGL_PLATFORM_ANGLE_TYPE_ANGLE, EGL_PLATFORM_ANGLE_TYPE_D3D11_ANGLE,
                        EGL_PLATFORM_ANGLE_MAX_VERSION_MAJOR_ANGLE, 9,
                        EGL_PLATFORM_ANGLE_MAX_VERSION_MINOR_ANGLE, 3,
                        EGL_ANGLE_DISPLAY_ALLOW_RENDER_TO_BACK_BUFFER, EGL_TRUE,
                        EGL_PLATFORM_ANGLE_ENABLE_AUTOMATIC_TRIM_ANGLE, EGL_TRUE,
                        EGL_NONE)),  
                  c_ints((EGL_PLATFORM_ANGLE_TYPE_ANGLE, EGL_PLATFORM_ANGLE_TYPE_D3D11_ANGLE,
                        EGL_PLATFORM_ANGLE_MAX_VERSION_MAJOR_ANGLE, 9,
                        EGL_PLATFORM_ANGLE_MAX_VERSION_MINOR_ANGLE, 3,
                        EGL_NONE)),
                  c_ints((EGL_PLATFORM_ANGLE_TYPE_ANGLE, EGL_PLATFORM_ANGLE_TYPE_D3D11_ANGLE,
                        EGL_PLATFORM_ANGLE_DEVICE_TYPE_ANGLE, EGL_PLATFORM_ANGLE_DEVICE_TYPE_WARP_ANGLE,
                        EGL_ANGLE_DISPLAY_ALLOW_RENDER_TO_BACK_BUFFER, EGL_TRUE,
                        EGL_PLATFORM_ANGLE_ENABLE_AUTOMATIC_TRIM_ANGLE, EGL_TRUE,
                        EGL_NONE)),  
                  c_ints((EGL_PLATFORM_ANGLE_TYPE_ANGLE, EGL_PLATFORM_ANGLE_TYPE_D3D11_ANGLE,
                        EGL_NONE)),
                  c_ints((EGL_PLATFORM_ANGLE_TYPE_ANGLE, EGL_PLATFORM_ANGLE_TYPE_D3D9_ANGLE,
                        EGL_NONE))]

i = 0
for a_list in attribute_lists:
  i += 1
  display = openegl.eglGetPlatformDisplayEXT(EGL_PLATFORM_ANGLE_ANGLE, 
                                            EGL_DEFAULT_DISPLAY, 
                                            ctypes.byref(a_list))
  if display == EGL_NO_DISPLAY:
    print("{} {}".format(i, display))
    continue
  r = openegl.eglInitialize(display, None, None)
  if r == EGL_TRUE:
    break

print("got to #{}/6 in a_list with display {}".format(i, display != EGL_NO_DISPLAY))

if display == EGL_NO_DISPLAY:
  display = openegl.eglGetDisplay(EGL_DEFAULT_DISPLAY)
  assert display != EGL_NO_DISPLAY #<<<<<<<<<<<<<<<<<<<<<<
  r = openegl.eglInitialize(display, None, None)
  assert r == EGL_TRUE             #<<<<<<<<<<<<<<<<<<<<<<

########## print out available configs #################################
attribute_list = c_ints([0 for i in range(60)])
config = ctypes.c_void_p()
numconfig = c_int()
val = c_int()
r = openegl.eglGetConfigs(display, ctypes.byref(attribute_list), 60, ctypes.byref(numconfig))
print("eglGetConfigs returned code=0x{:04X} with {} configs".format(r, numconfig.value)) # shouldn't be more than 60, surely!
for i in range(numconfig.value):
  conf_text = "\nconfig {}".format(i)
  for attr in egl_attr:
    r = openegl.eglGetConfigAttrib(display, attribute_list[i], egl_attr[attr], ctypes.byref(val))
    conf_text += ", {}={}".format(attr, val.value)
  print(conf_text)

######### run setup as near as poss done by DisplayOpenGL ##############
x = 0
y = 0
w = 0
h = 0
depth = 16
samples = 0

attribute_list = c_ints((EGL_RED_SIZE, 8,
                         EGL_GREEN_SIZE, 8,
                         EGL_BLUE_SIZE, 8,
                         EGL_DEPTH_SIZE, depth,
                         EGL_ALPHA_SIZE, 8,
                         EGL_BUFFER_SIZE, 32,
                         EGL_SAMPLES, samples, 
                         EGL_SURFACE_TYPE, EGL_WINDOW_BIT,
                         EGL_NONE))

r = openegl.eglChooseConfig(display,
                            ctypes.byref(attribute_list),
                            ctypes.byref(config), 1,
                            ctypes.byref(numconfig))
print("eglChoseCofnig returned {}".format(r))
context_attribs = c_ints((EGL_CONTEXT_CLIENT_VERSION, 2, EGL_NONE))
context = openegl.eglCreateContext(display, config,
                                        EGL_NO_CONTEXT, ctypes.byref(context_attribs) )

assert context != EGL_NO_CONTEXT #<<<<<<<<<<<<<

########################################################################
#Set the viewport position and size
dst_rect = c_ints((x, y, w, h))
src_rect = c_ints((x, y, w << 16, h << 16))

flags = pygame.RESIZABLE | pygame.OPENGL
wsize = (w, h)
if w == width and h == height: # i.e. full screen
  flags = pygame.FULLSCREEN | pygame.OPENGL
  wsize = (0, 0)
width, height = w, h
d = pygame.display.set_mode(wsize, flags)
window = pygame.display.get_wm_info()["window"]
surface = openegl.eglCreateWindowSurface(display, config, window, 0)
print("surface is {}".format(surface))
  
assert surface != EGL_NO_SURFACE #<<<<<<<<<<<<<
r = openegl.eglMakeCurrent(display, surface, surface, context)
assert r #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

#Create viewport
opengles.glViewport(0, 0, w, h)
########################################################################
opengles.glDepthRangef(c_float(0.0), c_float(1.0))
opengles.glClearColor (c_float(0.3), c_float(0.3), c_float(0.7), c_float(1.0))
opengles.glBindFramebuffer(GL_FRAMEBUFFER, 0)
#Setup default hints
opengles.glEnable(GL_CULL_FACE)
opengles.glEnable(GL_DEPTH_TEST)
opengles.glDepthFunc(GL_LESS);
opengles.glDepthMask(1);
opengles.glCullFace(GL_FRONT)
opengles.glHint(GL_GENERATE_MIPMAP_HINT, GL_NICEST)
opengles.glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
opengles.glColorMask(1, 1, 1, 0)
active = True
