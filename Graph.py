#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' Uses the pi3d.Graph class added to pi3d develop branch on Friday 13th Oct 2017
'''
import demo
import pi3d
import numpy as np

display = pi3d.Display.create(x=100, y=100)
font = pi3d.Font("fonts/NotoSerif-Regular.ttf")
key = pi3d.Keyboard()

x_vals = np.linspace(-30.0, 20.0, 500)
y_vals = np.zeros((2, 500))
f1, f2, f3 = 0.3, 0.4, 0.5
y_vals[0] = 0.18 * np.sin(x_vals * f1)
y_vals[1] = f2 + 0.2137 * np.cos(x_vals * f3)
W, H = 800, 600
xpos = -(display.width - W) / 2
ypos = (display.height - H) / 2

graph = pi3d.Graph(x_vals, y_vals, W, H, font, title='Snake Oil Production',
              xpos=xpos, ypos=ypos,
              axes_desc=['seconds', 'pints'], legend = ['viper', 'python'],
              ymax=1.2)

while display.loop_running():
  graph.draw()
  f1 = (f1 + 0.001) % 1.0
  f2 = (f2 + 0.0011) % 1.0
  f3 = (f3 + 0.005) % 2.0
  y_vals[0] = 0.18 * np.sin(x_vals * f1)
  y_vals[1] = f2 + 0.2137 * np.cos(x_vals * f3)
  graph.update(y_vals)
  if key.read() == 27:
    key.close()
    display.destroy()
    break
