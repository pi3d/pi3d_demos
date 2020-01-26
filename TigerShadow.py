#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals

""" TigerTank demo but with cast shadows
"""
import math, random, time, traceback

import demo
import pi3d

LOGGER = pi3d.Log(__name__, 'INFO')

# Create a Tkinter window
winw, winh, bord = 1200, 800, 0     #64MB GPU memory setting
# winw,winh,bord = 1920,1200,0   #128MB GPU memory setting

DISPLAY = pi3d.Display.create(tk=True, window_title='Tiger Tank demo in Pi3D',
                        w=winw, h=winh - bord, far=3000.0,
                        background=(0.4, 0.8, 0.8, 1), frames_per_second=16)

#inputs = InputEvents()
#inputs.get_mouse_movement()
CAMERA = pi3d.Camera()
CAM2D = pi3d.Camera(is_3d=False)

mylight = pi3d.Light(lightpos=(1.0, -1.0, 1.0), lightcol =(0.8, 0.8, 0.8), lightamb=(0.10, 0.10, 0.12))

win = DISPLAY.tkwin

shader = pi3d.Shader('shadow_uv_bump')
flatsh = pi3d.Shader('uv_flat')
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
mapwidth = 1800.0
mapdepth = 1800.0
mapheight = 120.0
mountimg1 = pi3d.Texture('textures/mountains3_512.jpg')
bumpimg = pi3d.Texture('textures/grasstile_n.jpg')
tigerbmp = pi3d.Texture('models/Tiger/tiger_bump.jpg')
topbmp = pi3d.Texture('models/Tiger/top_bump.jpg')
redb = pi3d.Texture('textures/red_ball.png', blend=True)
blub = pi3d.Texture('textures/blu_ball.png', blend=True)

mymap = pi3d.ElevationMap(mapfile='textures/mountainsHgt2.png',
                     width=mapwidth, depth=mapdepth,
                     height=mapheight, divx=64, divy=64)

mymap.set_draw_details(shader, [mountimg1, bumpimg], 128.0, 0.0)

FOG = (0.5, 0.5, 0.5, 0.8)

def set_fog(shape):
  shape.set_fog(FOG, 1000.0)

#Load tank
tank_body = pi3d.Model(file_string='models/Tiger/body.obj')
tank_body.set_shader(shader)
tank_body.set_normal_shine(tigerbmp)
""" NB the shadow texture must be the third texture in Buffer.textures
but OffscreenTextures textures don't exists until after they have been
drawn to. This isn't a problem where the textures can be passed to the
draw() method as with the ElevationMap see line 260. However for Model
drawing the diffuse texture is loaded automatically so the botch is to
check if there are still only two texttures and add the shadow map as
the third one see line 170
"""
tank_gun = pi3d.Model(file_string='models/Tiger/gun.obj')
tank_gun.set_shader(shader)

tank_turret = pi3d.Model(file_string='models/Tiger/turret.obj')
tank_turret.set_shader(shader)
tank_turret.set_normal_shine(topbmp)
### because these children will inherit matrix operation applied to
#   their parent they don't need to be scaled
tank_body.add_child(tank_turret)
tank_turret.add_child(tank_gun)

#Load church
x, z = 20, -320
y = mymap.calcHeight(x,z)

church = pi3d.Model(file_string='models/AllSaints/AllSaints.obj',
          sx=0.1, sy=0.1, sz=0.1, x=x, y=y, z=z)
church.set_shader(shader)

#Load cottages
x, z = 250,-40
y = mymap.calcHeight(x,z)

cottages = pi3d.Model(file_string='models/Cottages/cottages_low.obj',
          sx=0.1, sy=0.1, sz=0.1, x=x, y=y, z=z, ry=-5)
cottages.set_shader(shader)

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

#player tank vars
tankrot = 180.0
turret = 0.0
tankroll = 0.0     #side-to-side roll of tank on ground
tankpitch = 0.0   #too and fro pitch of tank on ground
enemyroll = 0.0
enemypitch = 0.0

#key presses
mymouse = pi3d.Mouse(restrict = False)
mymouse.start()
omx, omy = mymouse.position()

#position vars
mouserot = 0.0
tilt = 0.0
avhgt = 6.0
xm, oxm = 5.0, -1.0
zm, ozm = -185.0, -1.0
ym = mymap.calcHeight(xm, zm) + avhgt

#ShadowCaster
myshadows = pi3d.ShadowCaster([xm, ym, zm], mylight, scale=5.0)

#enemy tank vars
etx = 20
etz = -100
etr = 70.0

ltm = 0.0 #last pitch roll check
smode = False #sniper mode

def drawTiger(x, y, z, rot, roll, pitch, turret, gunangle, shadows=None):
  tank_body.position(x, y, z)
  tank_body.rotateToX(pitch)
  tank_body.rotateToY(rot)
  tank_body.rotateToZ(roll)
  tank_turret.rotateToY(turret - rot)
  tank_gun.rotateToZ(gunangle)
  if shadows == None:
    if len(tank_body.buf[0].textures) == 2: # i.e. first time drawn add shadow texture
      tank_body.buf[0].textures.append(myshadows)
      tank_turret.buf[0].textures.append(myshadows)
    tank_body.draw(light_camera=myshadows.LIGHT_CAM)
  else:
    shadows.cast_shadow(tank_body)

# Update display before we begin (user might have moved window)
win.update()

is_running = True

try:
  while DISPLAY.loop_running():
    mx, my = mymouse.position()
    mouserot -= (mx-omx)*0.2
    tilt += (my-omy)*0.2
    omx=mx
    omy=my

    CAMERA.reset()

    smmap.draw()
    dot1.position(HW + 200.0 * xm/mapwidth, HH + 200.0 * zm / mapdepth, 0.1)
    dot2.position(HW + 200.0 * etx/mapwidth, HH + 200.0 * etz / mapdepth, 0.05)
    dot1.draw()
    dot2.draw()

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
    CAMERA.position((xm + xoff, ym + yoff + 5, zm + zoff))
    oxm, ozm = xm, zm

    myshadows.start_cast([xm, ym, zm])
    #shadows player tank with smoothing on pitch and roll to lessen jerkiness
    drawTiger(xm, ym, zm, tankrot, tankroll, tankpitch, 180 - turret,
          (tilt*-2.0 if tilt > 0.0 else 0.0), shadows=myshadows)

    #shadows enemy tank
    difx = etx - xm # distance from self
    difz = etz - zm
    difd = (difx**2 + difz**2)**0.5
    detx = 1.0 * difz / difd - 0.005 * (difd - etr) * difx / difd
    detz = -1.0 * difx / difd - 0.005 * (difd - etr) * difz / difd
    etx += detx # gradually turns to circle player tank
    etz += detz
    #ety = mymap.calcHeight(etx, etz) + avhgt # see below
    etr += 0.5
    pitch, roll = mymap.pitch_roll(etx, etz)
    ety = mymap.ht_y + avhgt # calcHeight is now called as part of pitch_roll
    enemypitch = enemypitch * 0.9 + pitch * 0.1
    enemyroll = enemyroll * 0.9 + roll * 0.1
    drawTiger(etx, ety, etz, math.degrees(math.atan2(detx, detz)), enemyroll, enemypitch, 
              math.degrees(math.atan2(-detz, detx)), 0, shadows=myshadows)
    myshadows.cast_shadow(church)
    myshadows.cast_shadow(cottages)
    myshadows.cast_shadow(mymap)
    myshadows.end_cast()

    #Tanks and buildings for real
    drawTiger(xm, ym, zm, tankrot, tankroll, tankpitch, 180 - turret,
          (tilt*-2.0 if tilt > 0.0 else 0.0))
    drawTiger(etx, ety, etz, math.degrees(math.atan2(-detx, -detz)), roll, pitch, math.degrees(math.atan2(-detz, detx)), 0)
    church.draw()
    cottages.draw()

    #mymap.draw()           # Draw the landscape
    mymap.draw(shader, [mountimg1, bumpimg, myshadows], 128.0, 0.0, light_camera=myshadows.LIGHT_CAM)

    myecube.position(xm, ym, zm)
    myecube.draw()  #Draw environment cube

    if smode:
      """ because some of the overlays have blend=True they must be done AFTER
      other objects have been rendered.
      """
      target.draw()
      sniper.draw()
      
    # turns player tankt turret towards center of screen which will have a crosshairs
    if turret + 2.0 < mouserot:
      turret += 2.0
    if turret - 2.0 > mouserot:
      turret -= 2.0
    try:
      win.update()
    except Exception as e:
      LOGGER.info("bye,bye2 %s", e)
      myshadows.delete_buffers()
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
      mv = False
      if win.key == "w":
        xm -= math.sin(math.radians(tankrot)) * 2
        zm -= math.cos(math.radians(tankrot)) * 2
        mv = True
      elif win.key == "s":
        xm += math.sin(math.radians(tankrot)) * 2
        zm += math.cos(math.radians(tankrot)) * 2
        mv = True
      if win.key == "a":
        tankrot -= 2
      if win.key == "d":
        tankrot += 2
      if win.key == "p":
        pi3d.screenshot("TigerTank.jpg")
      if win.key == "Escape":
        try:
          LOGGER.info("bye,bye1")
          myshadows.delete_buffers()
          DISPLAY.destroy()
          try:
            win.destroy()
          except:
            pass
          mymouse.stop()
          exit()
        except:
          pass
      if mv: # moved so recalc pitch_roll
        pitch, roll = mymap.pitch_roll(xm, zm)
        tankpitch = tankpitch * 0.9 + pitch * 0.1
        tankroll = tankroll * 0.9 + roll * 0.1
        ym = mymap.ht_y + avhgt # calcHeight done by pitch_roll
    if win.ev=="drag" or win.ev=="click" or win.ev=="wheel":
      xm -= math.sin(math.radians(tankrot)) * 2
      zm -= math.cos(math.radians(tankrot)) * 2
      ym = (mymap.calcHeight(xm, zm) + avhgt)
    else:
      win.ev=""  #clear the event so it doesn't repeat

except Exception as e:
  LOGGER.info("bye,bye3 %s", e)
  myshadows.delete_buffers()
  DISPLAY.destroy()
  try:
    win.destroy()
  except:
    pass
  mymouse.stop()
  exit()
