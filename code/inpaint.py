#!/usr/bin/python3

import cv2 as cv
import numpy as np
import argparse

def diffusionStep(img, mask, kernel):
  diffused = cv.filter2D(img, -1, kernel)
  img = cv.bitwise_and(img, img, mask=cv.bitwise_not(mask))
  diffused = cv.bitwise_and(diffused, diffused, mask=mask)
  return img + diffused

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", required = True)
parser.add_argument("-m", "--maskFile", required = True)
parser.add_argument("-o", "--outputFile", required = True)
parser.add_argument("-n", "--iterations", type = int, required = True)

args = parser.parse_args()

kernel = np.array([[1.0 / 9, 1.0 / 9, 1.0 / 9],
                   [1.0 / 9, 1.0 / 9, 1.0 / 9],
                   [1.0 / 9, 1.0 / 9, 1.0 / 9]], np.float)

img = cv.imread(args.inputFile)
mask = cv.imread(args.maskFile)
mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
img = cv.bitwise_and(img, img, mask=cv.bitwise_not(mask))

for i in range(args.iterations):
  img = diffusionStep(img, mask, kernel)

cv.imwrite(args.outputFile, img)
