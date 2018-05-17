#!/usr/bin/python3

import cv2 as cv
import numpy as np
import argparse


def drawLines(img, horizLines, vertiLines, step = 1e3,
              colorHoriz = (0, 0, 255), colorVerti = (0, 127, 255), width = 1):
  lines = [(l[0], l[1], "H") for l in horizLines]
  lines += [(l[0], l[1], "V") for l in vertiLines]
  for rho, theta, direction in lines:
    midX, midY = rho * np.cos(theta), rho * np.sin(theta)
    lineAngle = theta - np.pi / 2
    p1X, p1Y = midX - step * np.cos(lineAngle), midY - step * np.sin(lineAngle)
    p2X, p2Y = midX + step * np.cos(lineAngle), midY + step * np.sin(lineAngle)
    p1 = (int(np.round(p1X)), int(np.round(p1Y)))
    p2 = (int(np.round(p2X)), int(np.round(p2Y)))
    color = colorHoriz if direction == "H" else colorVerti
    cv.line(img, p1, p2, color, width)


def classifyLines(lines, tolerance = 0.05):
  horizLines, vertiLines = [], []
  for rho, theta in lines:
    lineAngle = theta - np.pi / 2
    if -tolerance * np.pi < lineAngle < tolerance * np.pi:
      horizLines.append((rho, theta))
    if    (lineAngle < (-0.5 + tolerance) * np.pi
       or  lineAngle > (0.5 - tolerance) * np.pi):
      vertiLines.append((rho, theta))
  return (horizLines, vertiLines)


def intersectTwoLines(l1, l2):
  rho1, theta1 = l1
  rho2, theta2 = l2
  A = np.array([[np.cos(theta1), np.sin(theta1)],
                [np.cos(theta2), np.sin(theta2)]])
  b = np.array([[rho1], [rho2]])
  x, y = np.linalg.solve(A, b)
  x, y = int(np.round(x[0])), int(np.round(y[0]))
  return (x, y)


def intersectLines(linesA, linesB):
  return [intersectTwoLines(l1, l2) for l1 in linesA for l2 in linesB]


def drawPoints(img, points, color = (0, 255, 0), size = 2):
  for p in points:
    cv.line(img, p, p, color, size)


def classifyPoints(img, points, cornerSize = 0.2):
  height, width = img.shape[0], img.shape[1]
  topLeft = [p for p in points if 0 <= p[0] <= cornerSize * width
                              and 0 <= p[1] <= cornerSize* height]
  topLeft.append(np.array([0, 0]))
  topRight = [p for p in points if (1 - cornerSize) * width <= p[0] <= width
                               and 0 <= p[1] <= cornerSize * height]
  topRight.append(np.array([width, 0]))
  btmLeft = [p for p in points if 0 <= p[0] <= cornerSize * width
                              and (1 - cornerSize) * height <= p[1] <= height]
  btmLeft.append(np.array([0, height]))
  btmRight = [p for p in points if (1 - cornerSize) * width <= p[0] <= width
                               and (1 - cornerSize) * height <= p[1] <= height]
  btmRight.append(np.array([width, height]))
  return (topLeft, topRight, btmLeft, btmRight)


def cropRectangle(img, cornerPoints):
  distance = lambda p1, p2: np.linalg.norm(p1 - p2)
  height, width = img.shape[0], img.shape[1]
  topLeft, topRight = np.array([0, 0]), np.array([width, 0])
  btmLeft, btmRight = np.array([0, height]), np.array([width, height])
  topLeftPoints, topRightPoints, btmLeftPoints, btmRightPoints = cornerPoints
  topLeftPoint = max(topLeftPoints, key = lambda p : distance(p, topLeft))
  topRightPoint = max(topRightPoints, key = lambda p : distance(p, topRight))
  btmLeftPoint = max(btmLeftPoints, key = lambda p : distance(p, btmLeft))
  btmRightPoint = max(btmRightPoints, key = lambda p : distance(p, btmRight))
  minX = max(topLeftPoint[0], btmLeftPoint[0])
  maxX = min(topRightPoint[0], btmRightPoint[0])
  minY = max(topLeftPoint[1], topRightPoint[1])
  maxY = min(btmLeftPoint[1], btmRightPoint[1])
  cropTopLeft = (minX, minY)
  cropBtmRight = (maxX, maxY)
  return (cropTopLeft, cropBtmRight)


def cropImage(args):
  np.seterr(all = "ignore")
  img = cv.imread(args.inputFile)
  gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
  ret, thresh = cv.threshold(gray, args.threshold, 255, cv.THRESH_BINARY)
  edges = cv.Laplacian(thresh, 0)
  lines = cv.HoughLines(edges, args.rhoGranularity, args.thetaGranularity,
                        args.houghThreshold)
  lines = [l[0] for l in lines]
  horizLines, vertiLines = classifyLines(lines)
  intersections = intersectLines(horizLines, vertiLines)
  cornerPoints = classifyPoints(img, intersections)
  cropTopLeft, cropBtmRight = cropRectangle(img, cornerPoints)
  minX, minY = cropTopLeft
  maxX, maxY = cropBtmRight
  croppedImg = img.copy()[minY:maxY, minX:maxX]
  cv.imwrite(args.outputFile, croppedImg)
  
  if args.visualize:
    cropRectColor = (255, 0, 0)
    cropRectWidth = 1
    cv.imshow("gray", gray)
    cv.imshow("threshold", thresh)
    cv.imshow("edges", edges)
    drawLines(img, horizLines, vertiLines)
    drawPoints(img, intersections)
    cv.rectangle(img, cropTopLeft, cropBtmRight, cropRectColor, cropRectWidth)
    cv.imshow("image", img)
    cv.waitKey(0)


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", required = True)
parser.add_argument("-o", "--outputFile", required = True)
parser.add_argument("-v", "--visualize", action = "store_true")
parser.add_argument("-t", "--threshold", type = int, default = 110)
parser.add_argument("-rg", "--rhoGranularity", type = int, default = 1)
parser.add_argument("-tg", "--thetaGranularity", type = float, default = 0.001)
parser.add_argument("-ht", "--houghThreshold", type = int, default = 150)

args = parser.parse_args()
cropImage(args)
