from PIL import Image

root = 'map_tex'
im = Image.open('{}.png'.format(root))
for i in [0, 1, 2, 3 ,4]:
  for j in [0, 1, 2, 3 ,4]:
    l = (4 - i) * 32
    r = l + 33
    t = (4 - j) * 32
    b = t + 33
    sub_im = im.crop((l, t, r, b))
    sub_im.save('{}{}{}.png'.format(root, i, j))
