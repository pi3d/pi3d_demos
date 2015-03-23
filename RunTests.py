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

test_list = ["Amazing", "Blur", "CastShadows", "ClashWalk", "ClothWalk",
        "Clouds3d", "CollisionBalls", "Conway", "DogFight", "Earth",
        "EnvironmentSphere", "FilterDemo", "FixedString", "ForestQuickNumbers",
        "ForestWalk", "Gui", "IceGrow", "LoadModelObj", "LoadModelPickle",
        "MarsStation", "Minimal_2d", "Minimal", "NumpyBalls", "Orbit",
        "Pi3d2", "Pi3d3", "PictureFrame", "Pong", "Post", "ProceduralTerrain",
        "RobotWalkabout", "Scenery", "Shapes", "Silo", "Slideshow_2d",
        "Slideshow_3d", "Slideshow", "Snake", "TigerShadow", "TigerTank", "Water"]

for t in test_list:
  p = Popen([pyname, t + ".py"])
  print("\n\n{} >->".format(t))
  time.sleep(10.0)
  p.kill()

Popen(["stty", "sane"])
