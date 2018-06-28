import demo
import pi3d
import json

''' Demonstration of MergeShape using child objects as had to be done to
give different materials prior to pi3d v.2.22
 
ADP-glucose C16H25N5O15P2 from pubchem.ncbi.nlm.nih.gov
'''
with open('models/Structure3D_CID_16500.json','r') as f:
  json_data = json.load(f)['PC_Compounds'][0]
element = json_data['atoms']['element']
x = json_data['coords'][0]['conformers'][0]['x']
y = json_data['coords'][0]['conformers'][0]['y']
z = json_data['coords'][0]['conformers'][0]['z']
n = len(element)
'''NB if you download different molecules you might need to add to alter this.
 atomic number: name, radius, (r,g,b) tuple '''
atoms = {1:['hydrogen', 0.5, (1.0, 0.0, 0.0)],
         6:['carbon', 0.8, (0.1, 0.1, 0.1)],
         7:['nitrogen', 0.9, (0.1, 0.9, 1.0)],
         8:['oxygen', 0.9, (1.0, 1.0, 1.0)],
         15:['phosphorus', 1.5, (1.0, 0.0, 1.0)]}

display = pi3d.Display.create(frames_per_second=30)
camera = pi3d.Camera()

ball = pi3d.Sphere(radius=atoms[6][1])
carbon = pi3d.MergeShape(z=10)
for i in range(n):
  if element[i] == 6:
    carbon.add(ball, x[i], y[i], z[i])
carbon.set_material(atoms[6][2])
carbon.set_fog((0.3, 0.2, 0.6, 0.1), 18)

for e in atoms:
  if e != 6: # don't do carbon again
    ball = pi3d.Sphere(radius=atoms[e][1])
    elem = pi3d.MergeShape()
    for i in range(n):
      if element[i] == e:
        elem.add(ball, x[i], y[i], z[i])
    elem.set_material(atoms[e][2])
    elem.set_fog((0.3, 0.2, 0.6, 0.05), 18.9) # NB fog starts at 0.9 * 18.9, complete at 18.9
    carbon.add_child(elem)

# Fetch key presses -------   w move nearer, s move away, esc quit -----
keys = pi3d.Keyboard()
# Mouse -------------------   rotate molecule about y and x axes -------
mouse = pi3d.Mouse(restrict = False)
mouse.start()

while display.loop_running():
  carbon.draw()
  mx, my = mouse.position()
  carbon.rotateToY(mx)
  carbon.rotateToX(my)
  k = keys.read()
  if k != -1:
    if k == ord('w'):
      carbon.translateZ(-0.05)
    elif k == ord('s'):
      carbon.translateZ(0.05)
    elif k == 27:
      keys.close()
      display.destroy()
