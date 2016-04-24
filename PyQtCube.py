#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
''' Demo showing use of pi3d as a widget on a PyQt window. See PyQt documentation
for details on how to use that.
'''
import sys
import demo
import pi3d
import numpy as np
from PyQt4 import QtGui
from PyQt4 import QtCore

W, H = 640, 480
FPS = 20

class QtWindow(QtGui.QWidget):

  def __init__(self):
    super(QtWindow, self).__init__()
    ''' layer set to -128 to hide behind X desktop
    '''
    self.DISPLAY = pi3d.Display.create(w=W, h=H, layer=-128)
    shader = pi3d.Shader('uv_light')
    tex = pi3d.Texture('textures/PATRN.PNG')

    self.cube = pi3d.Cuboid(z=2)
    self.cube.set_draw_details(shader, [tex])
    self.cube.show_flag = True # additional attribute stuck onto Cuboid instance
    self.cube.last_x = None
    self.cube.last_y = None

    self.initUI() # not entirely sure why this is done in a different method, just copying others' code!
      
  def initUI(self):
    button1 = QtGui.QPushButton('Rotate X 5deg') # some jump rotations
    button1.clicked.connect(self.rotX)
    button2 = QtGui.QPushButton('Rotate Y 15deg')
    button2.clicked.connect(self.rotY)
    button3 = QtGui.QPushButton('Rotate Z 20deg')
    button3.clicked.connect(self.rotZ)
    message = QtGui.QLabel('Left click and\ndrag on image or\nclick these buttons')
    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(button1)
    vbox.addWidget(button2)
    vbox.addWidget(button3)
    vbox.addWidget(message)
    vbox.addStretch(1)
    self.img = QtGui.QLabel('image') # self. as needs to be accessed from outside this method
    a = np.zeros((H, W, 4), dtype=np.uint8)
    im = QtGui.QImage(a, W, H, QtGui.QImage.Format_RGB888)
    self.img.setPixmap(QtGui.QPixmap.fromImage(im))
    hbox = QtGui.QHBoxLayout()
    hbox.addLayout(vbox)
    hbox.addWidget(self.img)
    hbox.addStretch(1)
    self.setLayout(hbox)

    self.setWindowTitle('PyQT4 pi3d demo')
    self.show()
    
  def pi3d_loop(self):
    self.DISPLAY.loop_running()
    if self.cube.show_flag:
      self.cube.draw()
      im = QtGui.QImage(pi3d.screenshot(), W, H, QtGui.QImage.Format_RGB888)
      self.img.setPixmap(QtGui.QPixmap.fromImage(im))
      self.cube.show_flag = False
    
  def rotX(self):
    self.cube.rotateIncX(5.0)
    self.cube.show_flag = True

  def rotY(self):
    self.cube.rotateIncY(15.0)
    self.cube.show_flag = True

  def rotZ(self):
    self.cube.rotateIncZ(20.0)
    self.cube.show_flag = True

  def mousePressEvent(self, QMouseEvent):
    cursor = QtGui.QCursor()
    self.cube.last_x = cursor.pos().x()
    self.cube.last_y = cursor.pos().y()

  def mouseMoveEvent(self, QMouseEvent):
    cursor = QtGui.QCursor()
    x = cursor.pos().x()
    y = cursor.pos().y()
    self.cube.rotateIncY(self.cube.last_x - x)
    self.cube.rotateIncX(self.cube.last_y - y)
    self.cube.last_x = x
    self.cube.last_y = y
    self.cube.show_flag = True

app = QtGui.QApplication(sys.argv)
win = QtWindow()

timer = QtCore.QTimer()
timer.timeout.connect(win.pi3d_loop)
msfps = int(1000/FPS) # FPS in milliseconds
timer.start(msfps)

sys.exit(app.exec_())
