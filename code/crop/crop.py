import cv2 as cv
import numpy as np

def drawLines(img, lines):
  for rho,theta in lines:
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 10000*(-b))
    y1 = int(y0 + 10000*(a))
    x2 = int(x0 - 10000*(-b))
    y2 = int(y0 - 10000*(a))
    cv.line(img,(x1,y1),(x2,y2),(0,0,255),1)

def groupLines(lines):
  horiz = [l for l in lines if 0 <= l[1] <= 0.05 * np.pi or 0.95 * np.pi <= l[1] <= np.pi]
  verti = [l for l in lines if 0.45 * np.pi <= l[1] <= 0.55 * np.pi]
  return (horiz, verti)

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

def groupPoints(img, points):
  cornerSize = 0.2
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

def cropPoints(img, groups):
  height, width = img.shape[0], img.shape[1]
  topLeft, topRight = np.array([0, 0]), np.array([width, 0])
  btmLeft, btmRight = np.array([0, height]), np.array([width, height])
  topLeftPoint = max(groups[0], key = lambda p : np.linalg.norm(topLeft - p))
  topRightPoint = max(groups[1], key = lambda p : np.linalg.norm(topRight - p))
  btmLeftPoint = max(groups[2], key = lambda p : np.linalg.norm(btmLeft - p))
  btmRightPoint = max(groups[3], key = lambda p : np.linalg.norm(btmRight - p))
  topLeftPoint = (max(topLeftPoint[0], btmLeftPoint[0]), topLeftPoint[1])
  btmRightPoint = (min(topRightPoint[0], btmRightPoint[0]), btmRightPoint[1])
  return (topLeftPoint, btmRightPoint)

def drawPoints(img, points, color = (0, 255, 0), size = 2):
  for p in points:
    cv.line(img, p, p, color, size)

np.seterr(all = "ignore")
img = cv.imread("samples/sample1.jpg")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(gray, 100, 255, cv.THRESH_BINARY)
cv.imshow("thresh", thresh)
edges = cv.Canny(thresh, 70, 150)
#cv.imshow("edges", edges)
lines = cv.HoughLines(edges, 1, np.pi / 720, 150)
lines = [l[0] for l in lines] if lines is not None else []
horiz, verti = groupLines(lines)
points = intersectLines(horiz, verti)
corners = groupPoints(img, points)
drawPoints(img, points)
cropFrame = cropPoints(img, corners)
print(cropFrame)
cropImg = img.copy()[cropFrame[0][1]:cropFrame[1][1], cropFrame[0][0]:cropFrame[1][0]]
cv.rectangle(img, cropFrame[0], cropFrame[1], (0, 0, 255), 1)
cv.imshow("img", img)
#cv.imshow("crop", cropImg)
cv.waitKey(0)
