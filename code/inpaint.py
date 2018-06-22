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
parser.add_argument("-v", "--visualize", action = "store_true")

args = parser.parse_args()

kernel = np.array([[1.0 / 9, 1.0 / 9, 1.0 / 9],
                   [1.0 / 9, 1.0 / 9, 1.0 / 9],
                   [1.0 / 9, 1.0 / 9, 1.0 / 9]], np.float)

img = cv.imread(args.inputFile)
mask = cv.imread(args.maskFile)
mask = cv.cvtColor(mask, cv.COLOR_BGR2GRAY)
mask = cv.threshold(mask, 128, 255, cv.THRESH_BINARY)[1]
img = cv.bitwise_and(img, img, mask=cv.bitwise_not(mask))

for i in range(args.iterations):
  img = diffusionStep(img, mask, kernel)

if args.visualize:
  cv.imshow(args.outputFile, img)
  cv.waitKey(0)
else:
  cv.imwrite(args.outputFile, img)
