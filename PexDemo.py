#!/usr/bin/python

from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import pi3d

display = pi3d.Display.create(frames_per_second=30)
cam2D = pi3d.Camera(is_3d=False)
shader = pi3d.Shader('uv_flat')

keys = pi3d.Keyboard()

back = pi3d.ImageSprite('textures/straw1.jpg', shader=shader, w=display.width,
                        h=display.height, z=2000.0, camera=cam2D)

text = pi3d.FixedString('fonts/NotoSans-Regular.ttf', '''w,a,s,d move emitter location.
switch between different particles with space
esc to quit''',
    font_size=32, camera=cam2D, shader=shader, f_type='SMOOTH')
text.z = 150

particles = [pi3d.PexParticles('pex/jelly_fish.pex', camera=cam2D, z=100, emission_rate=40, scale=0.5),
            pi3d.PexParticles('pex/fire.pex', camera=cam2D, z=200, emission_rate=80),
            pi3d.PexParticles('pex/drugs.pex', camera=cam2D, z=300, emission_rate=30, rot_rate=2.0, rot_var=5.5),
            pi3d.PexParticles('pex/sun.pex', camera=cam2D, emission_rate=40)]
ix = 0
import time
tm = time.time()
n = 0
while display.loop_running():
  n += 1
  back.draw()
  text.draw()
  for p in particles:
    p.draw()
    if n % 2 == 0:
      p.update()

  k = keys.read()
  if k > -1:
    if k == ord(' '):
      ix = (ix + 1) % len(particles)
    p = particles[ix]
    if k == ord('a'):
      p.sourcePosition['x'] -= 10.0
    elif k == ord('d'):
      p.sourcePosition['x'] += 10.0
    elif k == ord('w'):
      p.sourcePosition['y'] += 10.0
    elif k == ord('s'):
      p.sourcePosition['y'] -= 10.0
    elif k == 27:
      keys.close()
      display.stop()
      break
print(n / (time.time() - tm))
