#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" An approximate testing system. Run with output piped into a text file:

  $ python3 RunTests.py > test_out.txt

errors should then be echod to the terminal while general logging output
gets put in the file.

NB this testing process won't necessarily pick up
faults with mouse or keyboard input or incorrect rendering of output.
"""

from subprocess import Popen, PIPE, STDOUT
import time
import sys

if sys.version_info[0] == 3: #i.e. will test with version used to start this program
  pyname = "python3"
else:
  pyname = "python"

FACTOR = 1.0 # increase for lower power i.e. on RPi A or B

test_list = [["Amazing", 10], ["Blur", 6], ["CastShadows", 6], ["ClashWalk", 6],
            ["ClothWalk", 6], ["Clouds3d", 5], ["CollisionBalls", 5],
            ["Conway", 5], ["DogFight", 10], ["Earth", 4], ["EnvironmentSphere", 4],
            ["FilterDemo", 10], ["FixedString", 4], ["ForestQuickNumbers", 6],
            ["ForestWalk", 6], ["Gui", 6], ["IceGrow", 6], ["LoadModelObj", 5],
            ["LoadModelPickle", 4], ["MarsStation", 12], ["Minimal_2d", 4],
            ["Minimal", 4], ["NumpyBalls", 5], ["Orbit", 5], ["Pi3d2", 4],
            ["Pi3d3", 4], ["PictureFrame", 10], ["Pong", 5], ["Post", 8],
            ["ProceduralTerrain", 10], ["RobotWalkabout", 8], ["Scenery", 10],
            ["Shapes", 5], ["Silo", 10], ["Slideshow_2d", 8], ["Slideshow_3d", 8],
            ["Slideshow", 8], ["Snake", 6], ["SpriteBalls", 6], ["TigerShadow", 10],
            ["TigerTank", 10], ["Water", 6]]

for t in test_list:
  p = Popen([pyname, t[0] + ".py"])
  print("\n\n{} >->".format(t))
  time.sleep(t[1] * FACTOR)
  p.kill()

Popen(["stty", "sane"])
