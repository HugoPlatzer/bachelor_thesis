#!/usr/bin/python3

import cv2 as cv
import numpy as np

def diffusionStep(img, mask, kernel):
  #~ diffused = cv.GaussianBlur(img, (5, 5), 0.5)
  diffused = cv.filter2D(img, -1, kernel)
  img = cv.bitwise_and(img, img, mask=cv.bitwise_not(mask))
  diffused = cv.bitwise_and(diffused, diffused, mask=mask)
  return img + diffused

#~ kernel = np.array([[0.0, 0.25, 0.0],
                   #~ [0.25, 0.0, 0.25],
                   #~ [0.0, 0.25, 0.0]], np.float)

#~ kernel = np.array([[0.38, 0.04, 0.04],
                   #~ [0.04, 0.00, 0.04],
                   #~ [0.04, 0.04, 0.38]], np.float)

kernel = np.array([[1.0 / 9, 1.0 / 9, 1.0 / 9],
                   [1.0 / 9, 1.0 / 9, 1.0 / 9],
                   [1.0 / 9, 1.0 / 9, 1.0 / 9]], np.float)

img = cv.imread("img13.png")
print(img.shape)
#~ img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
mask = cv.imread("img13_b.png")
mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
img = cv.bitwise_and(img, img, mask=cv.bitwise_not(mask))

for i in range(5000):
  print(i)
  img = diffusionStep(img, mask, kernel)

cv.imwrite("e1_out4.pnm", img)
#~ cv.waitKey(0)
