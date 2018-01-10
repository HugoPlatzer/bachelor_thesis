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

class Scanner():
  def __init__(self, parameters, processor):
    self.parameters = parameters
    self.processor = processor
    self.dev = usb.core.find(idVendor=0x05e3, idProduct=0x0145)

  def sendHeader(self):
    self.dev.ctrl_transfer(0x40, 12, 0x0088, 0, hb("ff"))
    self.dev.ctrl_transfer(0x40, 12, 0x0088, 0, hb("aa"))
    self.dev.ctrl_transfer(0x40, 12, 0x0088, 0, hb("55"))
    self.dev.ctrl_transfer(0x40, 12, 0x0088, 0, hb("00"))
    self.dev.ctrl_transfer(0x40, 12, 0x0088, 0, hb("ff"))
    self.dev.ctrl_transfer(0x40, 12, 0x0088, 0, hb("87"))
    self.dev.ctrl_transfer(0x40, 12, 0x0088, 0, hb("78"))
    self.dev.ctrl_transfer(0x40, 12, 0x0088, 0, hb("e0"))
    self.dev.ctrl_transfer(0x40, 12, 0x0087, 0, hb("05"))
    self.dev.ctrl_transfer(0x40, 12, 0x0087, 0, hb("04"))
    self.dev.ctrl_transfer(0x40, 12, 0x0088, 0, hb("ff"))

  def sendParameters(self, data):
    for b in data:
      self.dev.ctrl_transfer(0x40, 12, 0x0085, 0, bytearray([b]))

  def readResponse(self):
    responseA = self.dev.ctrl_transfer(0xc0, 12, 0x0084, 0, 1)[0]
    if responseA != 0x03:
      response = (responseA, None)
    else:
      responseB = self.dev.ctrl_transfer(0xc0, 12, 0x0084, 0, 1)[0]
      response = (responseA, responseB)
    print("device response: {}".format(response))
    return response

  def readBytesBulk(self, amount):
    print("readBytesBulk: amount = {}".format(amount))
    readRequest = bytearray([0x00, 0x00, 0x00, 0x00,
                             amount % 256, amount // 256, 0x00, 0x00])
    self.dev.ctrl_transfer(0x40, 4, 0x0082, 0, readRequest)
    return self.dev.read(0x81, amount, 10000)

  def initiateTransaction(self, parametersA):
    isReady = False
    while not isReady:
      self.sendHeader()
      self.sendParameters(parametersA)
      response = self.readResponse()
      isReady = (response != (0x03, 0x08))
      if not isReady:
        sleep(1.5)

  def basicTransaction(self, parametersA):
    debugStr = "basicTransaction: parametersA = {}"
    print(debugStr.format(parametersA.hex()))
    self.initiateTransaction(parametersA)
  
  def parameterTransaction(self, parametersA, parametersB):
    debugStr = "parameterTransaction: parametersA = {} parametersB = {}"
    print(debugStr.format(parametersA.hex(), parametersB.hex()))
    self.initiateTransaction(parametersA)
    self.sendParameters(parametersB)
    self.readResponse()

  def statusTransaction(self, parametersA):
    debugStr = "statusTransaction: parametersA = {}"
    print(debugStr.format(parametersA.hex()))
    amount = parametersA[3] * 256 + parametersA[4]
    self.initiateTransaction(parametersA)
    self.readBytesBulk(amount)
    self.readResponse()
  
  def imageTransaction(self, lines, amounts, processingFunction):
    debugStr = "imageTransaction: lines = {}, pattern = {}"
    print(debugStr.format(lines, amounts))
    parametersA = bytearray([0x08, 0x00, 0x00, 0x00, lines, 0x00])
    self.initiateTransaction(parametersA)
    for amount in amounts:
      data = self.readBytesBulk(amount)
      processingFunction(data)
    self.readResponse()
  
  def transactionAmounts(self, width, height, lines):
    size = width * lines
    numFFF0s = size // 0xfff0
    rest = size % 0xfff0
    amounts = [0xfff0] * numFFF0s
    if rest > 0:
      amounts.append(rest)
    return amounts
  
  def transferImage(self):
    transactionsFF = self.parameters["rawHeight"] // 0xff
    linesRest = self.parameters["rawHeight"] % 0xff
    amountsFF = self.transactionAmounts(self.parameters["rawWidth"],
                                         self.parameters["rawHeight"],
                                         0xff)
    amountsRest = self.transactionAmounts(self.parameters["rawWidth"],
                                          self.parameters["rawHeight"],
                                          linesRest)
    for i in range(transactionsFF):
      self.imageTransaction(0xff, amountsFF,
                            self.processor.appendImageBytes)
    if linesRest > 0:
      self.imageTransaction(linesRest, amountsRest,
                            self.processor.appendImageBytes)

  def scan(self):
    self.statusTransaction(hb("dd0000001200"))
    self.parameterTransaction(hb("0a0000000800"),
                              hb("1300040002006400"))
    self.parameterTransaction(hb("0a0000000800"),
                              hb("1300040004006400"))
    self.parameterTransaction(hb("0a0000000800"),
                              hb("1300040008006400"))
    self.parameterTransaction(hb("0a0000000800"),
                              hb("1400040002006400"))
    self.parameterTransaction(hb("0a0000000800"),
                              hb("1400040004006400"))
    self.parameterTransaction(hb("0a0000000800"),
                              hb("1400040008006400"))
    self.parameterTransaction(hb("0a0000000600"), hb("950000000000"))
    self.statusTransaction(hb("080000008000"))
    self.parameterTransaction(hb("0a0000000e00"),
                              self.parameters["str0A"])
    self.parameterTransaction(hb("0a0000000600"), hb("170002000100"))
    self.statusTransaction(hb("030000000e00"))
    self.basicTransaction(hb("000000000000"))
    self.statusTransaction(hb("d70000006700"))
    self.parameterTransaction(hb("dc0000001d00"),
                              self.parameters["strDC"])
    self.basicTransaction(hb("000000000000"))
    self.parameterTransaction(hb("150000001000"),
                              self.parameters["str15"])
    self.basicTransaction(hb("1b0000000100"))
    self.basicTransaction(hb("000000000000"))
    self.statusTransaction(hb("d70000006700"))
    self.parameterTransaction(hb("dc0000001d00"),
                              self.parameters["strDC"])
    self.imageTransaction(0x04, [0xa6e8],
                          self.processor.appendCalibrationBytes)
    self.basicTransaction(hb("000000000000"))
    self.imageTransaction(0xac, [0xfff0] * 28 + [0x0ab8],
                          self.processor.appendCalibrationBytes)
    self.statusTransaction(hb("d70000006700"))
    self.parameterTransaction(hb("dc0000001d00"),
                              self.parameters["strDC"])
    self.imageTransaction(0x04, [0xa6e8],
                          self.processor.appendCalibrationBytes)
    self.basicTransaction(hb("000000000000"))
    self.statusTransaction(hb("18000014dc00"))
    self.statusTransaction(hb("0f0000001200"))
    self.transferImage()
    self.processor.imageComplete()

class ScannerThread(QThread):
  def __init__(self, parameters, processor):
    super(ScannerThread, self).__init__()
    self.scanner = Scanner(parameters, processor)
    self.processor = processor

  def run(self):
    self.scanner.scan()

def main():
  app = QApplication([])
  window = ImageWidget((1652, 1060))
  processor = ImageProcessor(window)
  parameters = {"rawWidth" : 2 * 1653,
                "rawHeight" : 3204,
                "str0A" : hb("12000a0080006f02f0002829f819"),
                "strDC" : hb("7e26661c1515171411000000212121070000790b14000f000000000000"),
                "str15" : hb("000fb004802004000100000001801000")}
  feeder = ScannerThread(parameters, processor)
  feeder.start()
  
  window.showFullScreen()
  app.exec_()

main()
