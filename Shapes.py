#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Various standard shapes demonstrates different ways of setting draw details
either prior to or while drawing.
The demo also shows the way to import all the pi3d modules and using the String
and Font classes (see /usr/share/fonts/truetype/ for other fonts) The string
is a 3d object like the others. See the Blur demo for use of an orthographic (2D)
string object.
"""
# just allow this to run in a subdirectory
import demo
# Load *all* the classes
import pi3d
# Load diplay, nearly full screen
DISPLAY = pi3d.Display.create(x=20, y=20,
                        background=(0.0, 0.0, 0.1, 1.0), frames_per_second=30)
# Load shaders
shader = pi3d.Shader("uv_light")
shinesh = pi3d.Shader("uv_reflect")
flatsh = pi3d.Shader("uv_flat")
matsh = pi3d.Shader("mat_reflect")
##########################################
# Load textures
patimg = pi3d.Texture("textures/PATRN.PNG")
coffimg = pi3d.Texture("textures/COFFEE.PNG")
shapebump = pi3d.Texture("textures/floor_nm.jpg")
shapeshine = pi3d.Texture("textures/stars.jpg")
light = pi3d.Light(lightpos=(-1.0, 0.0, 10.0), lightcol=(3.0, 3.0, 2.0), lightamb=(0.02, 0.01, 0.03), is_point=True)

#Create inbuilt shapes
mysphere = pi3d.Sphere(radius=1, sides=24, slices=24, name="sphere",
        x=-4, y=2, z=10)
mytcone = pi3d.TCone(radiusBot=0.8, radiusTop=0.6, height=1, sides=24, name="TCone",
        x=-2, y=2, z=10)
myhelix = pi3d.Helix(radius=0.4, thickness=0.1, ringrots=12, sides=24, rise=1.5,
        loops=3.0, name="helix",x=0, y=2, z=10)
mytube = pi3d.Tube(radius=0.4, thickness=0.1, height=1.5, sides=24, name="tube",
        x=2, y=2, z=10, rx=30)
myextrude = pi3d.Extrude(path=((-0.5, 0.5), (0.5,0.7), (0.9,0.2),
        (0.2,0.05), (1.0,0.0), (0.5,-0.7), (-0.5, -0.5)), height=0.5, name="Extrude",
        x=4, y=2, z=10)
# Extrude can use three different textures if they are loaded prior to draw()
myextrude.set_shader(shinesh)
myextrude.buf[0].set_draw_details(shinesh, [coffimg, shapebump, shapeshine], 4.0, 0.2)
myextrude.buf[1].set_draw_details(shinesh, [patimg, shapebump, shapeshine], 4.0, 0.2)
myextrude.buf[2].set_draw_details(shinesh, [shapeshine, shapebump, shapeshine], 4.0, 0.2)

mycone = pi3d.Cone(radius=1, height=2, sides=24, name="Cone",
        x=-4, y=-1, z=10)
mycylinder = pi3d.Cylinder(radius=0.7, height=1.5, sides=24, name="Cyli",
        x=-2, y=-1, z=10)
# NB Lathe needs to start at the top otherwise normals are calculated in reverse,
# also inside surfaces need to be defined otherwise normals are wrong
mylathe = pi3d.Lathe(path=((0.0, 1.0), (0.6, 1.2), (0.8, 1.4), (1.09, 1.7),
                      (1.1, 1.7), (0.9, 1.4), (0.7, 1.2), (0.08, 1), (0.08, 0.21),
                      (0.1, 0.2), (1.0, 0.05), (1.0, 0.0), (0.001, 0.0), (0.0, 0.0)),
         sides=24, name="Cup", x=0, y=-1, z=10, sx=0.8, sy=0.8, sz=0.8)
mylathe.set_draw_details(matsh, [shapebump, shapeshine], 0.0, 1.0)
mylathe.set_alpha(0.3)
mytorus = pi3d.Torus(radius=1, thickness=0.3, ringrots=12, sides=24, name="Torus",
        x=2, y=-1, z=10)
myhemisphere = pi3d.Sphere(radius=1, sides=24, slices=24, hemi=0.5, name="hsphere",
        x=4, y=-1, z=10)
myPlane = pi3d.Plane(w=4, h=4, name="plane", z=12)

# Use three ttfs fonts one with the colour 'raspberry', one with background
# colour and one using a contrasting shadow
txt = "Now the Raspberry Pi really does rock"
strings = [pi3d.String(
            font=pi3d.Font("fonts/NotoSerif-Regular.ttf", (221, 0, 170, 255)), 
              string=txt, z=4),
           pi3d.String(
            font=pi3d.Font("fonts/NotoSerif-Regular.ttf", (0, 0, 26, 255)),
              string=txt, z=4),
           pi3d.String(
            font=pi3d.Font("fonts/NotoSerif-Regular.ttf", (0, 0, 26, 255),
                          background_color=(128, 128, 128, 0)),
              string=txt, z=4),
           pi3d.String(
            font=pi3d.Font("fonts/NotoSerif-Regular.ttf", (0, 0, 26, 255), 
                          shadow=(200, 255, 0, 255), shadow_radius=1), 
              string=txt, z=4)]

for s in strings:
  s.set_shader(flatsh)

# Fetch key presses
mykeys = pi3d.Keyboard()

angl = 0.0
i_f = 0
i_s = 0
# Display scene
while DISPLAY.loop_running():

  mysphere.draw(shader, [patimg])
  mysphere.rotateIncY(2.5)
  mysphere.rotateIncX(0.6101)

  myhemisphere.draw(shader, [coffimg])
  myhemisphere.rotateIncY( .5 )

  myhelix.draw(shader, [patimg])
  myhelix.rotateIncY(3)
  myhelix.rotateIncZ(1.1)

  mytube.draw(shinesh, [coffimg, shapebump, shapeshine], 4.0, 0.1)
  mytube.rotateIncY(3)
  mytube.rotateIncZ(2)

  # Extrude has different textures for each Buffer so has to use
  # set_draw_details() above, rather than having arguments passed to draw()
  myextrude.draw()
  myextrude.rotateIncY(-2)
  myextrude.rotateIncX(0.37)

  mycone.draw(shader, [coffimg])
  mycone.rotateIncY(-2)
  mycone.rotateIncZ(1)

  mycylinder.draw(shinesh, [patimg, shapebump, shapeshine], 4.0, 0.1)
  mycylinder.rotateIncY(2)
  mycylinder.rotateIncZ(1)

  mytcone.draw(shader, [coffimg])
  mytcone.rotateIncY(2)
  mytcone.rotateIncZ(-1)

  mytorus.draw(shinesh, [patimg, shapebump, shapeshine], 4.0, 0.3)
  mytorus.rotateIncY(3)
  mytorus.rotateIncZ(1)

  myPlane.draw(shader, [coffimg])
  myPlane.rotateIncX(3.1)

  mylathe.draw() # draw details set previously. NB after Plane as transparent
  mylathe.rotateIncY(0.2)
  mylathe.rotateIncZ(0.4)
  mylathe.rotateIncX(0.11)

  strings[i_s].draw()
  for s in strings:
    s.rotateIncZ(0.5)

  i_f += 1
  if i_f > 150:
    i_f = 0
    i_s = (i_s + 1) % len(strings) 

  k = mykeys.read()
  if k >-1:
    if k==112: pi3d.screenshot("shapesPic.jpg")
    elif k==27:
      mykeys.close()
      DISPLAY.destroy()
      break
