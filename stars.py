#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import pi3d
import time
import numpy as np

class Stars(object):
  def __init__(self):
    ''' The work of maintaining the visible stars at different locations while
    zooming around the galaxy has been delegated to this class
    '''
    self.v = []
    self.names = {} # most stars are unamed so it is more efficient to use a dictionary
    with open('models/hygdata001.csv','r') as f: # read the data from the file
      for i,l in enumerate(f.readlines()):
        ln = l.split(',')
        if ln[0] > '':
          self.names[i] = '' + ln[5] + ' ' + ln[0] # named star, prefix with constellation
        if ln[1] == '': # no blue value, use a mid
          ln[1] = '0.6'
        self.v.append([float(ln[2]), float(ln[4]), float(ln[3])] + # z and y swapped to OpenGL orientation.
                 self.bv2rgb(float(ln[1])) +
                 [float(vi) for vi in ln[6:7]] + [1.0 * i]) # last value is for index to names 

    self.v = np.array(self.v, dtype='float32') # and convert to ndarray
    self.xm, self.ym, self.zm = 0.2, 0.0, -2.0
    self.verts, self.norms, self.texs = None, None, None
    self.stars = None
    self.ready = False
    self.select_visible() # initial run, one off
    self.stars = pi3d.Points(vertices=self.verts, normals=self.norms, tex_coords=self.texs, point_size=15)
    starsh = pi3d.Shader("shaders/star_point") #shader uses rgb and luninosity
    self.stars.set_shader(starsh)

  def bv2rgb(self, bv):
    ''' convert blue value to rgb approximations. See
    http://stackoverflow.com/questions/21977786/ with thanks to @Spektre
    '''
    if bv < -0.4: bv = -0.4
    if bv > 2.0: bv = 2.0
    if bv >= -0.40 and bv < 0.00:
      t = (bv + 0.40) / (0.00 + 0.40)
      r = 0.61 + 0.11 * t + 0.1 * t * t
      g = 0.70 + 0.07 * t + 0.1 * t * t
      b = 1.0
    elif bv >= 0.00 and bv < 0.40:
      t = (bv - 0.00) / (0.40 - 0.00)
      r = 0.83 + (0.17 * t)
      g = 0.87 + (0.11 * t)
      b = 1.0
    elif bv >= 0.40 and bv < 1.60:
      t = (bv - 0.40) / (1.60 - 0.40)
      r = 1.0
      g = 0.98 - 0.16 * t
    else:
      t = (bv - 1.60) / (2.00 - 1.60)
      r = 1.0
      g = 0.82 - 0.5 * t * t
    if bv >= 0.40 and bv < 1.50:
      t = (bv - 0.40) / (1.50 - 0.40)
      b = 1.00 - 0.47 * t + 0.1 * t * t
    elif bv >= 1.50 and bv < 1.951:
      t = (bv - 1.50) / (1.94 - 1.50)
      b = 0.63 - 0.6 * t * t
    else:
      b = 0.0
    return [r, g, b]


  def select_visible(self):
    ''' this takes a subset of the total star array v and loads the locations
    into verts, the rgb values into norms, the luminance into texs[:,0] and
    the index number (for looking up the description) into texs[:,1]
      The selection is done on the basis of luminance divided by cartesian
    distance from the camera. The number selected is checked so that the
    size updated back to the Buffer.array_buffer is the same.
      The function is run the first time as a one off to create the initial
    stars object. Subsequently it runs in an infinite while loop in its own
    thread, checking every 2s and signalling to the main loop using the
    global 'ready' flag.
    '''
    while True:
      indx = np.where(self.v[:,6] / ((self.v[:,0] - self.xm) ** 2 + 
                                     (self.v[:,1] - self.ym) ** 2 + 
                                     (self.v[:,2] - self.zm) ** 2) > 0.002)
      if self.verts is None:
        self.verts = np.zeros((len(indx[0]), 3), dtype='float32')
        self.norms = np.zeros((len(indx[0]), 3), dtype='float32')
        self.texs = np.zeros((len(indx[0]), 2), dtype='float32')
      nv = min(len(self.verts), len(indx[0]))
      self.verts[:nv] = self.v[indx[0],0:3][:nv]
      self.norms[:nv] = self.v[indx[0],3:6][:nv]
      self.texs[:nv] = self.v[indx[0],6:8][:nv]
      if self.stars is not None:
        self.ready = True
      else:
        return # do first time blocking execution
      time.sleep(2.0)
  
  def draw(self):
    self.stars.draw()

  def re_init(self):
    # have to do this in main thread, i.e. can't be just included in select_visible
    self.stars.re_init(pts=self.verts, normals=self.norms, texcoords=self.texs)
    self.ready = False

