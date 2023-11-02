#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Example similar to CollisionBalls but with proximity calcualtion much
speeded up using numpy and rendering speeded up using glScissor
"""

import random
import sys
import numpy as np

import demo
import pi3d
from pi3d.sprite.ScissorBall import ScissorBall

MAX_BALLS = 25
MIN_BALL_SIZE = 5
MAX_BALL_SIZE = 40
MAX_BALL_VELOCITY = 10.0

LOGGER = pi3d.Log(__name__, level='INFO')

BACKGROUND_COLOR = (1.0, 1.0, 1.0, 0.0)
DISPLAY = pi3d.Display.create(background=BACKGROUND_COLOR, frames_per_second=30, use_sdl2=True)
KEYBOARD = pi3d.Keyboard()
WIDTH, HEIGHT = DISPLAY.width, DISPLAY.height
CAMERA = pi3d.Camera(is_3d=False)
SHADER = pi3d.Shader('uv_flat')

TEXTURE_NAMES = ['textures/red_ball.png',
                 'textures/grn_ball.png',
                 'textures/blu_ball.png']
TEXTURES = [pi3d.Texture(t) for t in TEXTURE_NAMES]

def random_ball(b):
  """Return a ball with a random color, position and velocity."""
  return ScissorBall(camera=CAMERA, shader=SHADER,
                   texture=TEXTURES[int(3 * b / MAX_BALLS) % 3],
                   radius=random.uniform(MIN_BALL_SIZE, MAX_BALL_SIZE),
                   x=random.uniform(-WIDTH / 2.0, WIDTH / 2.0),
                   y=random.uniform(-HEIGHT / 2.0, HEIGHT / 2.0),
                   vx=random.uniform(-MAX_BALL_VELOCITY, MAX_BALL_VELOCITY),
                   vy=random.uniform(-MAX_BALL_VELOCITY, MAX_BALL_VELOCITY))


SPRITES = [random_ball(b) for b in range(MAX_BALLS)]

RADII = np.array([[s.radius + i.radius for s in SPRITES] for i in SPRITES])

LOGGER.info('Starting NumpyBalls')

while DISPLAY.loop_running():
  a = np.array([b.unif[0:3] for b in SPRITES])
  b = np.copy(a)
  d0 = a[:,0].reshape(1,-1).T - b[:,0]
  d1 = a[:,1].reshape(1,-1).T - b[:,1]
  d3 = (d0 ** 2 + d1 ** 2) ** 0.5 - RADII
  
  for i in range(0, MAX_BALLS):
    for j in range(i + 1, MAX_BALLS):
      if d3[i][j] < 0:
        SPRITES[i].bounce_collision(SPRITES[j])
    SPRITES[i].repaint(0 if i == (MAX_BALLS - 1) else 1)

  if KEYBOARD.read() == 27:
    DISPLAY.stop()
