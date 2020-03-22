#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" An approximate testing system. Run with output piped into a text file:

  $ python3 RunTests.py > test_out.txt

errors should then be echod to the terminal while general logging output
gets put in the file.

NB this testing process won't necessarily pick up
faults with mouse or keyboard input or incorrect rendering of output.
"""

from subprocess import run, Popen, PIPE, STDOUT
import time
import sys

if len(sys.argv) > 1: #can put a python interpreter name on the end to force i.e. using pypy
  pyname = sys.argv[1]
else:
  if sys.version_info[0] == 3: #i.e. will test with version used to start this program
    pyname = "python3"
  else:
    pyname = "python"

FACTOR = 1.0 # increase for lower power i.e. 0.5 on x86/64, 1.0 Pi3/4/5, 2.0 on Pi A or B
# these should now be in order of increasing complexity
test_list = [["Minimal", 4], ["Minimal_2d", 4], ["Clouds3d", 5], ["LoadModelObj", 5],
              ["Shapes", 5], ["Water", 6], ["Snake", 6], ["LoadModelPickle", 5],
              ["ForestWalk", 6], ["ForestQuickNumbers", 6], ["MarsStation", 13],
              ["RobotWalkabout", 8], ["CollisionBalls", 5], ["Slideshow_2d", 6],
              ["Amazing", 10], ["ClothWalk", 6], ["Earth", 4], ["EnvironmentSphere", 5],
              ["FixedString", 5], ["PictureFrame", 7], ["Pong", 5],["Orbit", 5],
              ["Silo", 10], ["TigerTank", 10], ["Post", 6], ["FilterDemo", 10], ["Billboard", 6],
              ["Blur", 6], ["CastShadows", 6], ["StringMulti", 6], ["Polygon", 4],
              ["ClashWalk", 6], ["Conway", 5], ["DogFight", 10],
              ["ForestStereo", 6], ["Gui", 6], ["IceGrow", 6], ["NumpyBalls", 5],
              ["PexDemo", 3], ["Pi3d3", 4], ["TigerShadow", 10], ["ProceduralTerrain", 6],
              ["Scenery", 15], ["SpriteBalls", 6], ["SpriteMulti", 6]
            ]

for t in test_list:
  p = Popen([pyname, t[0] + ".py"])
  print("\n\n{} >->".format(t))
  time.sleep(t[1] * FACTOR)
  p.kill()

Popen(["stty", "sane"])
