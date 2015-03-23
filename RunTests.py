#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
from subprocess import Popen, PIPE, STDOUT
import time
import sys

if sys.version_info[0] == 3:
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

import curses
curses.nocbreak()
key = curses.initscr()
key.keypad(0)
curses.echo()
curses.endwin()
