#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Loading or saving a model from or to a pickled form. The initial
model is loaded using Wavefront obj model loading as in LoadModelObj.py.

KEY 'd' will save the model as models/teapot.pkl and subsequent runs of the
program will load from that file.

Loading is much faster from a pickled file but the size is quite a bit
bigger; in this demo 282k+7k+37k+36k => 1.5M in python3 or 4.6M in python2
This is almost certainly because of the images, so with larger images it
may be worth pickling without the Textures and adding these after loading.
"""
import demo
import pi3d
# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100,
                         background=(0.2, 0.4, 0.6, 1), frames_per_second=30)
shader = pi3d.Shader("uv_reflect")
#========================================
# this is a bit of a one off because the texture has transparent parts
# comment out and google to see why it's included here.
pi3d.opengles.glDisable(pi3d.GL_CULL_FACE)
#========================================

# load model
try:
  with open('models/teapot.pkl', 'rb') as f: #python3 requires binary
    import pickle
    mymodel = pickle.load(f)
except Exception as e:
  print("""    exception was {} - could be IOError for missing file or various errors from trying to
  load a file pickled with a different version of python or pickle etc
  'd' to save this model as pickle file""".format(e))
# load bump and reflection textures
  bumptex = pi3d.Texture("textures/floor_nm.jpg")
  shinetex = pi3d.Texture("textures/stars.jpg")
  mymodel = pi3d.Model(file_string='models/teapot.obj', name='teapot', z=4.0)
  mymodel.set_normal_shine(bumptex, 16.0, shinetex, 0.5)
mymodel.set_shader(shader)

# Fetch key presses
mykeys = pi3d.Keyboard()

while DISPLAY.loop_running():
  mymodel.draw()
  mymodel.rotateIncY(0.41)
  mymodel.rotateIncZ(0.12)
  mymodel.rotateIncX(0.23)

  k = mykeys.read()
  if k >-1:
    if k==112:
      pi3d.screenshot('teapot.jpg')
    elif k == ord('d'):
      import pickle
      with open('models/teapot.pkl', 'wb') as f:
        pickle.dump(mymodel, f)
    elif k==27:
      mykeys.close()
      DISPLAY.destroy()
      break
