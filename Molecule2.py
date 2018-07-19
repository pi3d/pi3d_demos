import demo
import pi3d
import json

''' Demonstration of MergeShape using a single object with multiple Buffers,
each with different material as can be done from pi3d v.2.22
 
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
 atomic number: name, radius, (r,g,b) tuple, Buffer num (NB this last value
 not used in the Molecule1 demo)'''
atoms = [[1, 'hydrogen', 0.5, (1.0, 0.0, 0.0), 0],
         [6, 'carbon', 0.8, (0.1, 0.1, 0.1), 1],
         [7, 'nitrogen', 0.9, (0.1, 0.9, 1.0), 2],
         [8, 'oxygen', 0.9, (1.0, 1.0, 1.0), 3],
         [15, 'phosphorus', 1.5, (1.0, 0.0, 1.0), 4]]

display = pi3d.Display.create(frames_per_second=30)
camera = pi3d.Camera()

ball = pi3d.Sphere()
ball.set_shader(pi3d.Shader('mat_light'))
molecule = pi3d.MergeShape(z=10)
molecule.set_fog((0.3, 0.2, 0.6, 0.05), 18.9) # NB fog starts at 0.9 * 18.9, complete at 18.9

for a in atoms:
  ball.set_material(a[3])
  buflist = []
  for i in range(n):
    if a[0] == element[i]:
      # merge scale values used for atom size
      buflist.append([ball, x[i], y[i], z[i], 0.0, 0.0, 0.0,
                        a[2], a[2], a[2], a[4]])
  molecule.merge(buflist)

# Fetch key presses -------   w move nearer, s move away, esc quit -----
keys = pi3d.Keyboard()
# Mouse -------------------   rotate molecule about y and x axes -------
mouse = pi3d.Mouse(restrict = False)
mouse.start()

while display.loop_running():
  molecule.draw()
  mx, my = mouse.position()
  molecule.rotateToY(mx)
  molecule.rotateToX(my)
  k = keys.read()
  if k != -1:
    if k == ord('w'):
      molecule.translateZ(-0.05)
    elif k == ord('s'):
      molecule.translateZ(0.05)
    elif k == 27:
      keys.close()
      display.destroy()
