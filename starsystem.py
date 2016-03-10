#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

import demo
import pi3d

class StarSystem(object):
  def __init__(self, star_ref, planet_tex, obj_object, v):
    ''' 
    '''
    self.flatsh = pi3d.Shader('uv_flat')
    self.shader = pi3d.Shader('uv_light')
    self.star_tex = pi3d.Texture('textures/sun.jpg')
    self.star = None
    self.planet = None
    self.change_details(star_ref, planet_tex, obj_object, v)
    self.visible = True

  def draw(self):
    if self.visible:
      self.star.draw()
      self.planet.draw()
      self.obj_object.draw()
    self.planet.rotateIncY(-0.05)
    self.obj_object.rotateIncY(0.1)
    self.obj_object.rotateIncZ(0.07)
    
  def change_details(self, star_ref, planet_tex, obj_object, v):
    self.star_ref = star_ref
    star_loc = v[star_ref,0:3]
    star_rgb = v[star_ref,3:6]
    light = pi3d.Light(is_point=True, lightpos=star_loc, lightcol=star_rgb*15.0,
                            lightamb=(0.01, 0.01, 0.01))
    if self.star is None:
      self.star = pi3d.Sphere(radius=0.4, slices=24, sides=24)
      self.star.set_draw_details(self.flatsh, [self.star_tex])
    self.star.set_material(star_rgb)
    self.star.position(*star_loc)

    if self.planet is None:
      self.planet = pi3d.Sphere(radius=0.1, slices=24, sides=24, light=light)
      self.planet.set_shader(self.shader)
    self.planet.set_textures([planet_tex])
    self.planet.set_light(light)
    self.planet.position(star_loc[0], star_loc[1], star_loc[2]-2.2)

    self.obj_object = obj_object
    self.obj_object.set_shader(self.shader)
    self.obj_object.set_light(light)
    self.obj_object.position(star_loc[0]+0.2, star_loc[1], star_loc[2]-1.75)

systems = [[0, pi3d.Texture("textures/world_map.jpg"), pi3d.Model(file_string='models/biplane.obj', sx=0.01, sy=0.01, sz=0.01)]]
'''
pumpkin = pi3d.Model(file_string='models/pumpkin.obj', sx=0.01, sy=0.01, sz=0.01)
tardis = pi3d.Model(file_string='models/Tardis.obj', sx=0.002, sy=0.002, sz=0.002)
iss = pi3d.Model(file_string='models/iss.obj', sx=0.04, sy=0.04, sz=0.04)

systems = [[0, pi3d.Texture("textures/mars.jpg"), iss],
           [17025, pi3d.Texture("textures/planet01.png"), tardis],
           [71408, pi3d.Texture("textures/planet02.png"), pumpkin],
           [42572, pi3d.Texture("textures/planet03.jpg"), pumpkin],
           [35897, pi3d.Texture("textures/planet04.jpg"), pumpkin],
           [5454, pi3d.Texture("textures/planet05.png"), tardis],
           [9, pi3d.Texture("textures/planet06.png"), tardis],
           [3476, pi3d.Texture("textures/planet07.jpg"), tardis],
           [24245, pi3d.Texture("textures/planet08.png"), tardis],
           [102488, pi3d.Texture("textures/planet09.jpg"), tardis],
           [32928, pi3d.Texture("textures/planet10.jpg"), iss]]
'''


