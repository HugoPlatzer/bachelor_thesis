#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import usb.core
from time import time, sleep
from datetime import datetime

def hb(hexStr):
  return bytearray.fromhex(hexStr)

class ImageWidget(QLabel):
  updateRow = pyqtSignal(int, bytearray)
  imageComplete = pyqtSignal()
  
  def _updateRow(self, i, line):
    print("updateRow {}".format(i))
    lineSize = self.image.width() * 4
    offset = lineSize * i
    self.imagePtr[offset:offset + lineSize] = line
    self._updatePixmap()

  def _updatePixmap(self):
    self.setPixmap(QPixmap.fromImage(self.image))

  def resizeEvent(self, event):
    self._updatePixmap()  

  def saveImage(self):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    self.image.save("scan_{}.png".format(timestamp))
  
  def __init__(self, imageSize, parent = None):
    super(ImageWidget, self).__init__()
    self.setScaledContents(True)
    self.image = QImage(*imageSize, QImage.Format_ARGB32)
    self.image.fill(0x12345678)
    self.imagePtr = self.image.bits()
    self.imagePtr.setsize(self.image.byteCount())
    self.updateRow.connect(self._updateRow)
    self.imageComplete.connect(self.saveImage)
    self.setMinimumSize(100, 100)
    self.setScaledContents(True)
    self.setCursor(Qt.BlankCursor)

class ImageProcessor():
  byteBuffer = bytearray()
  lineSize = 2 * 1653
  channelPattern = ["r", "g", "b"]
  inLinesCount = 0
  channelOffsets = {"r" : 2, "g" : 5, "b" : 8}
  inLinesDropped = {"r" : 0, "g" : 0, "b" : 0}
  inLines = {"r" : [], "g" : [], "b" : []}
  outLinesCount = 0
  valueMap = bytearray()
  gamma = 0.5
  
  def __init__(self, widget):
    self.widget = widget
    for i in range(256):
      self.valueMap.append(self.processValue(i))
  
  def processValue(self, v):
    v = round(255.0 * ((v / 255.0) ** self.gamma))
    return min(max(v, 0), 255)
  
  def processLine(self, line):
    patternIdx = self.inLinesCount % len(self.channelPattern)
    channel = self.channelPattern[patternIdx]
    if self.inLinesDropped[channel] < self.channelOffsets[channel]:
      self.inLinesDropped[channel] += 1
      return
    
    line = line[3::2]
    line = bytearray(self.valueMap[v] for v in line)
    self.inLines[channel].append(line)
  
  def mergeChannels(self, r, g, b):
    return (0xff << 24) + (r << 16) + (g << 8) + b
  
  def mergeChannelLines(self):
    while all(len(self.inLines[c]) > 0 for c in ["r", "g", "b"]):
      lineR = self.inLines["r"].pop(0)
      lineG = self.inLines["g"].pop(0)
      lineB = self.inLines["b"].pop(0)
      outLine = bytearray()
      for i in range(len(lineR)):
        outLine.append(lineB[i])
        outLine.append(lineG[i])
        outLine.append(lineR[i])
        outLine.append(0xff)
      self.widget.updateRow.emit(self.outLinesCount, outLine)
      self.outLinesCount += 1

  def appendCalibrationBytes(self, data):
    print("received {} calibration bytes".format(len(data)))

  def appendImageBytes(self, data):
    print("received {} image bytes".format(len(data)))
    t1 = time()
    self.byteBuffer += data
    while len(self.byteBuffer) >= self.lineSize:
      self.processLine(self.byteBuffer[:self.lineSize])
      self.mergeChannelLines()
      self.inLinesCount += 1
      self.byteBuffer = self.byteBuffer[self.lineSize:]
    t2 = time()
    print("processing took {:.1f} ms".format(1000 * (t2 - t1)))

  def imageComplete(self):
    self.widget.imageComplete.emit()

class DummyFeeder(QThread):
  def __init__(self, processor):
    super(DummyFeeder, self).__init__()
    self.processor = processor

  def run(self):
    with open("../captures/succ2/d1_i.bin", "rb") as f:
      data = f.read()
    while len(data) > 0:
      sleep(0.05)
      chunk = data[:65520]
      data = data[65520:]
      self.processor.appendImageBytes(chunk)

def main():
  app = QApplication([])
  window = ImageWidget((1652, 1060))
  processor = ImageProcessor(window)
  feeder = DummyFeeder(processor)
  feeder.start()
  
  window.showFullScreen()
  app.exec_()

main()

