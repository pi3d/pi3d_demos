#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Example of using the loop control in the Display class with the behaviour
included in the pi3d.sprites.Ball class
"""

import random
import sys
import math

import demo
import pi3d

MAX_BALLS = 25
MIN_BALL_SIZE = 5
MAX_BALL_SIZE = 40
MAX_BALL_VELOCITY = 10.0

BACKGROUND_COLOR = (1.0, 1.0, 1.0, 0.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=30)
WIDTH, HEIGHT = DISPLAY.width, DISPLAY.height
ZPLANE = 1000
fov = 2.0 * math.degrees(math.atan(HEIGHT/2.0/ZPLANE))
# logger created before other pi3d components to allow logging, NB no name set
LOGGER = pi3d.Log(level='INFO') #, file='temp.txt') # to file to see log with ncurses keyboard

KEYBOARD = pi3d.Keyboard()

CAMERA = pi3d.Camera((0, 0, 0), (0, 0, -1.0),
                (1, 1100, fov,
                 WIDTH / float(HEIGHT)))
SHADER = pi3d.Shader('uv_flat')

TEXTURE_NAMES = ['textures/red_ball.png',
                 'textures/grn_ball.png',
                 'textures/blu_ball.png']
TEXTURES = [pi3d.Texture(t) for t in TEXTURE_NAMES]

def random_ball(b):
  """Return a ball with a random color, position and velocity."""
  return pi3d.Ball(shader=SHADER,
                   texture=TEXTURES[int(3 * b / MAX_BALLS) % 3],
                   radius=random.uniform(MIN_BALL_SIZE, MAX_BALL_SIZE),
                   x=random.uniform(-WIDTH / 2.0, WIDTH / 2.0),
                   y=random.uniform(-HEIGHT / 2.0, HEIGHT / 2.0), z=ZPLANE,
                   vx=random.uniform(-MAX_BALL_VELOCITY, MAX_BALL_VELOCITY),
                   vy=random.uniform(-MAX_BALL_VELOCITY, MAX_BALL_VELOCITY))


SPRITES = [random_ball(b) for b in range(MAX_BALLS)]
DISPLAY.add_sprites(*SPRITES)

LOGGER.info('Starting CollisionBalls')

while DISPLAY.loop_running():
  for i, ball1 in enumerate(SPRITES):
    for ball2 in SPRITES[0:i]:
      ball1.bounce_collision(ball2)

  if KEYBOARD.read() == 27:
    DISPLAY.stop()
