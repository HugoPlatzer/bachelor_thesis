#!/usr/bin/python
from PIL import Image
import numpy as np

img = Image.open("samples/sample1b.jpg")
pixels = img.load()
stepSize = 2

for x in range(0, img.size[0], stepSize):
  for y in range(0, img.size[1], stepSize):
    frame = (x, y,
             min(x + stepSize, img.size[0]),
             min(y + stepSize, img.size[1]))
    print(frame)
    i2 = img.crop(frame)
    print(i2.size)
    a = np.array(i2.getdata())
    aVar = np.var(a)
    v = int(aVar / 10)
    for x2 in range(frame[0], frame[2]):
      for y2 in range(frame[1], frame[3]):
        pixels[x2, y2] = (v, v, v)

img.show()
