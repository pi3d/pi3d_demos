#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Strings rendered using 
Font - For generating a font drawn with gl_point and recoloured using
 shader uv_pointsprite

FastText - Manages the collection of data for all of the strings to be drawn.
  Enables drawing all strings in one pass.
  
TextBlock - A string which has its content, position, size, rotation, colour, alpha,
 character positioning, justification etc.. defined by this.

"""

print("""
ESC to quit
""")

import numpy as np
import random

import demo
import pi3d

import os
import math
import time


""" An example class to contain some data to display, showing how the
FastText class can be be passed object and attributes rather than plain
text. If the text represented by the attribute changes then the block will
be regenerated when FastText.regen() is called. 
"""
class EgClass(object):
  valA = 0.0
  fps = 0.0
  strA = "A moving string"

eg_object = EgClass() # create an instance of the example class

KEYBOARD = pi3d.Keyboard()
LOGGER = pi3d.Log.logger(__name__)

BACKGROUND_COLOR = (0.0, 0.0, 0.0, 0.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=30)
HWIDTH, HHEIGHT = DISPLAY.width / 2.0, DISPLAY.height / 2.0

QWIDTH = HWIDTH/2 # quarter width

CAMERA = pi3d.Camera(is_3d=False)

font_colour = (255,255,255,255)

text_pos = QWIDTH

working_directory = os.path.dirname(os.path.realpath(__file__))
font_path = os.path.abspath(os.path.join(working_directory, 'fonts', 'FreeSans.ttf'))

# Create pointFont and the text manager to use it
pointFont = pi3d.Font(font_path, font_colour, codepoints=list(range(32,128)), font_size=48)
text = pi3d.FastText(pointFont, CAMERA, max_chars=200)

#Basic static text
newtxt = pi3d.TextBlock(-100, -50, 0.1, 0.0, 14, text_format="Static string",
          size=0.9, spacing="F", space=0.05, colour=(0.0, 1.0, 0.0, 1.0) )
text.add_text_block(newtxt)

"""The next three strings are formated with data from an object.  When the
object data changes and the text block is regenerated, the string is
changed to the new data values."""
moving_text = pi3d.TextBlock(0, 0, 0.1, 0.0, 25, eg_object, "strA",
          text_format="{:s}", size=0.6, spacing="F", space=0.08,
          colour=(1.0, 0.0, 0.0, 1.0) )
text.add_text_block(moving_text)

newtxt = pi3d.TextBlock(-150, 75, 0.1, 0.0, 18, eg_object, "valA",
          text_format="number: {:4.3f}", size=0.5, spacing="F", space=0.05,
          colour=(0.0, 0.0, 1.0, 1.0) )
text.add_text_block(newtxt)

newtxt = pi3d.TextBlock(200, -200, 0.1, 0.0, 10, eg_object, "fps",
          text_format="fps:{:2.1f}", size=0.75, spacing="C", space=0.6,
          colour=(0.0, 1.0, 1.0, 1.0) )
text.add_text_block(newtxt)


textSize = 0.1
sizingText = pi3d.TextBlock(-100, 150, 0.1, 0.0, 15,
          text_format="Resizing text", size=textSize, spacing="F",
          space=0.05, colour=(1.0, 1.0, 0.0, 1.0) )
text.add_text_block(sizingText)

# String rotation and spacing
textRotation = 0.0
rotatingText = pi3d.TextBlock(-200, -150, 0.1, textRotation, 15,
          text_format="Rotating text", size=0.7, spacing="C", space=0.6,
          colour=(1.0, 1.0, 1.0, 0.5), justify=0.5 )
text.add_text_block(rotatingText)

rotatingChars = pi3d.TextBlock(-300, -100, 0.1, 0.0, 15,
          text_format="Rotating chars", size=0.6, spacing="C", space=0.6,
          colour=(0.99, 0.5, 0.5, 1.0) )
text.add_text_block(rotatingChars)

spacingText = pi3d.TextBlock(-350, -300, 0.1, 0.0, 10, text_format="Spacing",
          size=0.7, spacing="C", space=0.1, colour=(0.5, 1.0, 0.5, 1.0) )
text.add_text_block(spacingText)

#String colour and alpha
textAlpha = 0.1
alphaText = pi3d.TextBlock(-250, -300, 0.0, 90.0, 15, text_format="Alpha change",
          size=0.99, spacing="C", space=0.6, colour=(0.99, 0.99, 0.99, textAlpha) )
text.add_text_block(alphaText)

colourText = pi3d.TextBlock(-300, -200, 1.0, 0.0, 15, text_format="Colour change",
          size=0.8, spacing="C", space=0.6, colour=(0.99, 0.5, 0.5, 1.0) )
text.add_text_block(colourText)

gradientText = pi3d.TextBlock(50, -250, 0.1, 0.0, 16, text_format="Colour Gradient",
          size=0.7, spacing="C", space=0.6, colour=(0.5, 1.0, 0.5, 1.0) )
text.add_text_block(gradientText)
gradientText.set_colour_gradient((1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 0.0), 1.0, 1.0)

alphaGradientText = pi3d.TextBlock(50, -100, 0.1, 0.0, 16, text_format="Alpha Gradient",
          size=0.7, spacing="C", space=0.6, colour=(0.5, 1.0, 0.5, 1.0) )
text.add_text_block(alphaGradientText)
alphaGradientText.set_colour_gradient((1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, 0.0), 1.0, 0.25)

frame_count = 0
end_time = time.time() + 1.0

while DISPLAY.loop_running():
  text_pos -= 3
  if text_pos < -QWIDTH:
    text_pos = QWIDTH
  moving_text.set_position(x=text_pos)
  eg_object.valA += 0.01
  eg_object.valA *= 1.0123
  if eg_object.valA > 1000.0:
    eg_object.valA *= 0.01
    
  textSize += 0.01
  if textSize > 0.99:
    textSize = 0.1
 
  sizingText.set_text(size=textSize)
  
  textRotation += 1.0
  if textRotation >= 180.0:
    textRotation -= 360.0
    
  rotatingText.set_position(rot=textRotation)
  rotatingChars.set_text(char_rot=textRotation)
  
  textAlpha += 0.01
  if textAlpha >= 1.0:
    textAlpha = 0.1
  alphaText.set_colour(alpha=textAlpha)
  
  colour_angle = math.radians(textRotation)
  red = math.cos(colour_angle)
  blue = math.cos(colour_angle + (math.pi * 0.666) )  
  green = math.cos(colour_angle + (math.pi * 1.333) )  
  colour = [red, green , blue, 1.0]
  colourText.set_colour(colour)
  
  spacingText.set_text(space=textSize)
  
  now = time.time()
  frame_count += 1
  if now > end_time:
    end_time = now + 1.0
    eg_object.fps = frame_count
    frame_count = 0
    if eg_object.strA == "A moving string":
      eg_object.strA = "String moving"
    else: 
      eg_object.strA = "A moving string"

  text.regen()
  text.draw()
  

  k = KEYBOARD.read()
  if k > -1:
    if k == 27:
      KEYBOARD.close()
      DISPLAY.stop()
      break
