#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" Landscape from ElevationMap with model tanks and buildings. Demonstrates using
a function to draw the various parts of the tank and the ElevationMap.pitch_roll()
method to make models conform (aproximately) to the surface of an ElevationMap.

Also look out for:

Parent-child Shapes. The tank gun is a child of the turret which is a child
of the body. The gun is raised as the mouse view points to looking up by rotating
about its local x axis. The turret rotates about its local y axis. This shows how to
combine various rotations about different axes without the objects falling apart!

Note that the origin for all three component Shapes of the tank model is
at the pivot point of the turret. However for the gun the rotation is moved
to the front edge of the turret by using cz=2.5 in the constructor.

In order for the missiles to be fired from the tanks correctly this demo
shows the use of Shape.transform_direction() which generate a 3D vector
representing the direction of the gun in global space. This is used to provide
launch velocity for the missiles which are then rotated to align with their
current velocity (on their parabola) using Shape.rotate_to_direction()

The Shape.shallow_clone() method has been used to make mulitple copies of
the tanks and missiles. This creates instances of the position, rotation,
scale etc properties of the Shape but shares the mesh and texture data.

Rather than use the normal methods for positioning and rotating shapes the
@property and associated setter methods have been used Shape.xyz and Shape.rxryrz

2D shader usage. Drawing onto an ImageSprite canvas placed in front of the camera
imediately after reset() This is used to generate a splash screed during file
loading and to draw a telescopic site view and a navigation map with the locations
of the tanks.

The ElevationMap uses the uv_elev_map shader which allow four diffuse and
four normal textures to be mapped to the terrain.

This demo also uses a tkinter tkwindow but creates it as method of Display. Compare
with the system used in demos/MarsStation.py

Tip: u raises gun, j lowers gun, f fires gun
"""
import math, random, time, traceback

import demo
import pi3d

LOGGER = pi3d.Log(__name__, level='INFO')

# Create a Tkinter window
winw, winh, bord = 1200, 600, 0     #64MB GPU memory setting
# winw,winh,bord = 1920,1200,0   #128MB GPU memory setting

DISPLAY = pi3d.Display.create(tk=True, window_title='Tiger Tank demo in Pi3D',
                        w=winw, h=winh - bord, far=3000.0,
                        background=(0.4, 0.8, 0.8, 1), frames_per_second=16)

#inputs = InputEvents()
#inputs.get_mouse_movement()
CAMERA = pi3d.Camera()
CAM2D = pi3d.Camera(is_3d=False)
pi3d.Light(lightpos=(-1, -1, 1), lightcol =(0.8, 0.8, 0.8), lightamb=(0.30, 0.30, 0.32))

win = DISPLAY.tkwin

shader = pi3d.Shader('uv_bump')
mapshader = pi3d.Shader("uv_elev_map")
flatsh = pi3d.Shader('uv_flat')
matsh = pi3d.Shader('mat_light')
shade2d = pi3d.Shader('2d_flat')

#========================================
# create splash screen and draw it
splash = pi3d.ImageSprite("textures/tiger_splash.jpg", shade2d, w=10, h=10, z=0.2)
splash.draw()
DISPLAY.swap_buffers()

# create environment cube
ectex = pi3d.loadECfiles('textures/ecubes/Miramar', 'miramar_256',
                                    suffix='png')
myecube = pi3d.EnvironmentCube(size=1800.0, maptype='FACES')
myecube.set_draw_details(flatsh, ectex)

# Create elevation map
mapwidth = 2000.0
mapdepth = 2000.0
mapheight = 100.0
mountimg1 = pi3d.Texture('textures/mountains3_512.jpg')
roadimg = pi3d.Texture('textures/Roof.png')
grassimg = pi3d.Texture('textures/grass.jpg')
rockimg = pi3d.Texture('textures/rock1.jpg')
redb = pi3d.Texture('textures/red_ball.png', blend=True)
blub = pi3d.Texture('textures/blu_ball.png', blend=True)

# normal textures
tigerbmp = pi3d.Texture('models/Tiger/tiger_bump.jpg')
topbmp = pi3d.Texture('models/Tiger/top_bump.jpg')
mudbmp = pi3d.Texture('textures/mudnormal.jpg')
grassbmp = pi3d.Texture('textures/grasstile_n.jpg')
rockbmp = pi3d.Texture('textures/rocktile2.jpg')

mymap = pi3d.ElevationMap(mapfile='textures/mountainsHgt2.png',
                     width=mapwidth, depth=mapdepth,
                     height=mapheight, divx=64, divy=64, texmap='textures/roads.jpg')

mymap.set_draw_details(mapshader, [grassimg, grassbmp,
                                rockimg, rockbmp, 
                                mountimg1, rockbmp,
                                roadimg, mudbmp], 64.0, 0.0, umult=48.0, vmult=48.0)

FOG = (0.5, 0.5, 0.5, 0.8)

mymap.set_fog(FOG, 800.0)

#Load tank
tank_body = pi3d.Model(file_string='models/Tiger/body.obj')
tank_body.set_shader(shader)
tank_body.set_normal_shine(tigerbmp)
tank_body.set_fog(FOG, 800.0)

tank_gun = pi3d.Model(file_string='models/Tiger/gun.obj', z=0.2, cz=2.5)
tank_gun.set_shader(shader)
tank_body.set_fog(FOG, 800.0)

tank_turret = pi3d.Model(file_string='models/Tiger/turret.obj')
tank_turret.set_shader(shader)
tank_turret.set_normal_shine(topbmp)
tank_turret.set_fog(FOG, 800.0)

#Make some clones of this tank
tanks = [] # will be a list of lists [body, turret, gun] to allow articulation
tanks.append([tank_body, tank_turret, tank_gun]) # tanks[0] will be the one driven by the user
for i in range(3): # try increasing to see the limitations of pi3d, python, GPU and CPU
  tanks.append([tank_body.shallow_clone(), None, None])
  tanks[-1][1] = tank_turret.shallow_clone()
  tanks[-1][2] = tank_gun.shallow_clone()
  tanks[-1][0].xyz = (random.random() * 800.0 - 400.0, 0.0, random.random() * 600.0 - 100.0)
### because these children will inherit matrix operation applied to
#   their parent they don't need to be scaled
#   as these are cloned the child references get duplicated if add_child()
#   is used so the children attribute has to be overwritten with a new list (of one)
for t in tanks:
  t[0].children = [t[1]] #turret is child of body
  t[1].children = [t[2]] #gun is child of turret

#Make some missiles
missile = pi3d.Lathe(path=((0.0, 1.5), (0.1, 1.5), (0.13, 0.7),
                (0.2, 0.6), (0.2, 0.01), (0.19, 0.0), (0.0, 0.0)), sides=12)
missile.set_material((1.0, 0.0, 1.0)) # purple beer bottle!
missile.set_shader(matsh) # mat_light is default if nothing specified better to be explicit

missiles = [] # will be list of missiles
for t in tanks:
  missiles.append(missile.shallow_clone())
  missiles[-1].x_vel = 0.0 # add velocity attributes to the instance
  missiles[-1].y_vel = -5.0 # this may or may not be good practice but
  missiles[-1].z_vel = 0.0 # python allows it so why not...
  missiles[-1].next_tm = 0.0 # also add next fire time to missiles to restrict fire rate
  missiles[-1].expl = 0.0 # also add exploding factor

#Load church
x, z = 20, -320
y = mymap.calcHeight(x,z)

church = pi3d.Model(file_string='models/AllSaints/AllSaints.obj',
          sx=0.1, sy=0.1, sz=0.1, x=x, y=y, z=z)
church.set_shader(shader)
church.set_fog(FOG, 800.0)

#Load cottages
x, z = 250,-40
y = mymap.calcHeight(x,z)

cottages = pi3d.Model(file_string='models/Cottages/cottages_low.obj',
          sx=0.1, sy=0.1, sz=0.1, x=x, y=y, z=z, ry=-5)
cottages.set_shader(shader)
cottages.set_fog(FOG, 800.0)

#cross-hairs in gun sight
targtex = pi3d.Texture("textures/target.png", blend=True)
target = pi3d.ImageSprite(targtex, shade2d, w=10, h=10, z=0.4)
target.set_2d_size(targtex.ix, targtex.iy, (DISPLAY.width - targtex.ix)/2,
                  (DISPLAY.height - targtex.iy)/2)

#telescopic gun sight
sniptex = pi3d.Texture("textures/snipermode.png", blend=True)
sniper = pi3d.ImageSprite(sniptex, shade2d, w=10, h=10, z=0.3)
scx = DISPLAY.width/sniptex.ix
scy = DISPLAY.height/sniptex.iy
if scy > scx:
  scx = scy # enlarge to fill screen but use same scale for both directions
scw, sch = sniptex.ix * scx, sniptex.iy * scx
sniper.set_2d_size(scw, sch, (DISPLAY.width - scw)/2,(DISPLAY.height - sch)/2)

#corner map and dots
HW, HH = (DISPLAY.width - 200.0) / 2, (DISPLAY.height - 200.0) / 2
smmap = pi3d.ImageSprite(mountimg1, flatsh, w=200, h=200, 
            x=HW, y=HH, z=0.2, camera=CAM2D)
dot1 = pi3d.ImageSprite(redb, flatsh, w=10, h=10, z=0.1, camera=CAM2D)
dot2 = pi3d.ImageSprite(blub, flatsh, w=10, h=10, z=0.05, camera=CAM2D)

#key presses
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()
omx, omy = mymouse.position()

#position vars
mouserot = 0.0
tilt = 0.0
avhgt = 6.0
xm, oxm = 0.0, -1.0
zm, ozm = -200.0, -1.0
ym = mymap.calcHeight(xm, zm) + avhgt
tankrot, tankpitch, tankroll = 180.0, 0.0, 0.0
turret = 0.0
elev = 0.0

ltm = 0.0 #last pitch roll check
smode = False #sniper mode

def limit_tilt(tilt):
  return elev + ((tilt - 5) if tilt > 5.0 else 0.0)

win.update()

is_running = True
#try:
while DISPLAY.loop_running():
      mx, my = mymouse.position()
      mouserot -= (mx-omx)*0.2
      tilt += (my-omy)*0.2
      omx=mx
      omy=my

      CAMERA.reset()

      smmap.draw()
      for t in tanks[1:]: # all the enemy dots will be the same colour
        dot2.xyz = (HW + 200.0 * t[0].x() / mapwidth, HH + 200.0 * t[0].z() / mapdepth, 0.05)
        dot2.draw()
      dot1.xyz = (HW + 200.0 * xm/mapwidth, HH + 200.0 * zm / mapdepth, 0.1)
      dot1.draw()

      # tilt can be used to prevent the view from going under the landscape!
      sf = 60 - 55.0 / abs(tilt) if tilt < -1 else 5.0
      xoff = sf * math.sin(math.radians(mouserot))
      yoff = abs(1.25 * sf * math.sin(math.radians(tilt))) + 3.0
      zoff = -sf * math.cos(math.radians(mouserot))

      if tilt > -5 and smode == False: # zoom in
        CAMERA.reset(lens=(1, 3000, 12.5, DISPLAY.width / DISPLAY.height))
        smode = True
      elif tilt <= -5 and smode == True: # zoom out
        CAMERA.reset(lens=(1, 3000, 45, DISPLAY.width / DISPLAY.height))
        smode = False

      #adjust CAMERA position in and out so we can see our tank
      CAMERA.rotate(tilt, mouserot, 0)
      CAMERA.position((xm + xoff, ym + yoff + 5.0, zm + zoff))
      oxm, ozm = xm, zm

      mymap.draw() # Draw the landscape first as tank wheels have transparency

      for i, t in enumerate(tanks):
        b_x, b_y, b_z = t[0].xyz
        b_rx, b_ry, b_rz = t[0].rxryrz
        t_rx, t_ry, t_rz = t[1].rxryrz
        g_rx, g_ry, g_rz = t[2].rxryrz
        if i == 0: # this is your tank
          b_x, b_z = xm, zm
          ym = b_y # as y value set later and ym is used for camera
          tgt_x, tgt_z = b_x, b_z # other tanks will use tanks[0] as target!
          b_ry = tankrot
          t_ry = 180 + turret - tankrot
          g_rx = limit_tilt(tilt)
        else: # these are enemies
          manhatten_dist = abs(tgt_x - b_x) + abs(tgt_z - b_z) # approx so they're not too accurate
          b_x -= 0.5 * math.sin(math.radians(b_ry))
          b_z -= 0.5 * math.cos(math.radians(b_ry))
          rot_to = math.degrees(math.atan2(tgt_x - b_x, tgt_z - b_z))
          # use tweening for rotation and add an error depending on dist and i
          # this remainder method avoids weirdness as rot_to goes from 0 to 360
          b_ry += ((rot_to + 7.5 * i + 3000.0 / manhatten_dist - b_ry) % 360 - 180) * 0.05
          t_ry = 180 + rot_to - b_ry # point straight as us!
          g_rx = min(45.0, max(0.0, manhatten_dist * 0.2))
        pitch, roll = mymap.pitch_roll(b_x, b_z)
        b_y = mymap.ht_y + avhgt # calcHeight is now called as part of pitch_roll
        b_rx = b_rx * 0.9 + pitch * 0.1
        b_rz = b_rz * 0.9 + roll * 0.1

        t[0].xyz = (b_x, b_y, b_z) # set position
        t[0].rxryrz = (b_rx, b_ry, b_rz) # set rotations. Body
        t[1].rxryrz = (t_rx, t_ry, t_rz) # turret
        t[2].rxryrz = (g_rx, g_ry, g_rz) # gun
        t[0].draw()

      for i, m in enumerate(missiles):
        m_x, m_y, m_z = m.xyz
        tm = time.time()
        terrain_ht = mymap.calcHeight(m_x, m_z)
        if m_y < terrain_ht:
          #print(i, tm, m.next_tm)
          # dropped through the floor, go back to gun and get launch direction
          if tm > m.next_tm: # if long enough gap, re-fire missile
            # NB vectors are scaled by the parent scale factor
            m.next_tm = tm + 10.0
            # the gun is actually pointing -z direction. move up 2 so 
            but_pt, aim_vec = tanks[i][2].transform_direction([0.0, 0.0, -1.0],
                                                              [0.0, 0.0, 0.0])
            m.xyz = but_pt + aim_vec * 12.0 # start from about muzzle
            m.x_vel, m.y_vel, m.z_vel = aim_vec * 3.0
            m.expl = 0.0 # stop exploding
            m.sxsysz = (1.0, 1.0, 1.0) # return to normal size
            m.set_point_size(0.0) # back to normal polygon drawing
          elif m.expl < 99.5: # keep exploding until reach size or time is up
            m.expl = 50 + m.expl * 0.5 # explode fast then slow 
            m.sxsysz = (m.expl, m.expl, m.expl)
            m.set_point_size(500.0) # draw vertices as points (size at one unit of distance from camera)
            m.draw()
        else:
          m.y_vel -= 0.03 # downward acc gravity
          # the missile created by Lathe is pointing upwards so use up vector
          # also have to reverse x, not sure why
          m.rotate_to_direction([-m.x_vel, m.y_vel, m.z_vel], [0.0, 1.0, 0.0])
          m.xyz = (m_x + m.x_vel, m_y + m.y_vel, m_z + m.z_vel)
          m.draw()
          # approx hit detection
          for j, t in enumerate(tanks):
            if i != j:
              t_x, t_y, t_z = t[0].xyz
              if abs(m_x - t_x) < 10 and abs(m_y - t_y) < 4 and abs(m_z - t_z) < 10:
                o_x, o_y, o_z = tanks[i][0].xyz
                dist = ((o_x - t_x) ** 2 + (o_y - t_y) ** 2 + (o_z - t_z) ** 2) ** 0.5
                print('tank #{} hit tank #{} at a range of {:5.1f}'.format(i, j, dist))
                m.xyz = m_x, terrain_ht - 0.1, m_z # stop multiple hits!

      #Draw buildings
      church.draw()
      cottages.draw()

      myecube.xyz = (xm, ym, zm)
      myecube.draw()  #Draw environment cube

      if smode:
        """ because some of the overlays have blend=True they must be done AFTER
        other objects have been rendered.
        """
        target.draw()
        sniper.draw()

      # turns player tank turret towards center of screen which will have a crosshairs
      if turret + 2.0 < -mouserot:
        turret += 2.0
      if turret - 2.0 > -mouserot:
        turret -= 2.0

      try:
        win.update()
      except Exception as e:
        LOGGER.info("bye,bye2 %s", e)
        DISPLAY.destroy()
        try:
          win.destroy()
        except:
          pass
        mymouse.stop()
        exit()
      if win.ev == "resized":
        LOGGER.info("resized")
        DISPLAY.resize(win.winx, win.winy, win.width, win.height-bord)
        CAMERA.reset((DISPLAY.near, DISPLAY.far, DISPLAY.fov,
                    DISPLAY.width / float(DISPLAY.height)))
        win.resized = False
      if win.ev == "key":
        if win.key == "w":
          xm -= math.sin(math.radians(tankrot)) * 2
          zm -= math.cos(math.radians(tankrot)) * 2
        elif win.key == "s":
          xm += math.sin(math.radians(tankrot)) * 2
          zm += math.cos(math.radians(tankrot)) * 2
        elif win.key == "a":
          tankrot -= 2
        elif win.key == "d":
          tankrot += 2
        elif win.key == "f": # fire on space
          missiles[0].positionY(-100.0)
          missiles[0].next_tm = 0.0
        elif win.key == "p":
          pi3d.screenshot("TigerTank.jpg")
        elif win.key == "u":
          elev += 5
        elif win.key == "j":
          elev -= 5
        elif win.key == "Escape":
          try:
            LOGGER.info("bye,bye1")
            DISPLAY.destroy()
            try:
              win.destroy()
            except:
              pass
            mymouse.stop()
            exit()
          except:
            pass
      if win.ev=="drag" or win.ev=="click" or win.ev=="wheel":
        xm -= math.sin(math.radians(tankrot)) * 2
        zm -= math.cos(math.radians(tankrot)) * 2
        ym = (mymap.calcHeight(xm, zm) + avhgt)
      else:
        win.ev=""  #clear the event so it doesn't repeat
'''
except Exception as e:
  LOGGER.info("bye,bye3 %s", e)
  DISPLAY.destroy()
  try:
    win.destroy()
  except:
    pass
  mymouse.stop()
  exit()'''
