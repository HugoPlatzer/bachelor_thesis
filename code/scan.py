#!/usr/bin/python3

# Control the Reflecta CrystalScan 7200 film scanner

import argparse
import usb.core
from time import sleep
from array import array

parser = argparse.ArgumentParser()
args = parser.parse_args()

def hb(hexStr):
  return bytearray.fromhex(hexStr)

def assertDeviceResponse(byte):
  response = dev.ctrl_transfer(0xc0, 12, 0x0084, 0, 1)
  if response[0] != byte:
    print("unexpected response: {}".format(response))
    #raise Exception("unexpected response: {}".format(response))

def checkDeviceReady():
  assertDeviceResponse(0x03)
  response = dev.ctrl_transfer(0xc0, 12, 0x0084, 0, 1)
  return (response[0] == 0x00)

def sendHeader():
  dev.ctrl_transfer(0x40, 12, 0x0088, 0, bytearray.fromhex("ff"))
  dev.ctrl_transfer(0x40, 12, 0x0088, 0, bytearray.fromhex("aa"))
  dev.ctrl_transfer(0x40, 12, 0x0088, 0, bytearray.fromhex("55"))
  dev.ctrl_transfer(0x40, 12, 0x0088, 0, bytearray.fromhex("00"))
  dev.ctrl_transfer(0x40, 12, 0x0088, 0, bytearray.fromhex("ff"))
  dev.ctrl_transfer(0x40, 12, 0x0088, 0, bytearray.fromhex("87"))
  dev.ctrl_transfer(0x40, 12, 0x0088, 0, bytearray.fromhex("78"))
  dev.ctrl_transfer(0x40, 12, 0x0088, 0, bytearray.fromhex("e0"))
  dev.ctrl_transfer(0x40, 12, 0x0087, 0, bytearray.fromhex("05"))
  dev.ctrl_transfer(0x40, 12, 0x0087, 0, bytearray.fromhex("04"))
  dev.ctrl_transfer(0x40, 12, 0x0088, 0, bytearray.fromhex("ff"))

def sendParameters(data):
  for b in data:
    dev.ctrl_transfer(0x40, 12, 0x0085, 0, bytearray([b]))

def basicTransfer(bytesA):
  sendHeader()
  sendParameters(bytesA)
  while not checkDeviceReady():
    sleep(1.5)
    sendHeader()
    sendParameters(bytesA)

def extraParameterTransfer(bytesA, bytesB):
  sendHeader()
  sendParameters(bytesA)
  assertDeviceResponse(0x00)
  sendParameters(bytesB)
  assertDeviceResponse(0x03)
  assertDeviceResponse(0x00)

def readBytesBulk(amount):
  readRequest = bytearray([0, 0, 0, 0, amount % 256, amount // 256, 0, 0])
  dev.ctrl_transfer(0x40, 4, 0x0082, 0, readRequest)
  return dev.read(0x81, amount, -1)

def statusReadTransfer(bytesA):
  amount = bytesA[3] * 256 + bytesA[4]
  sendHeader()
  sendParameters(bytesA)
  assertDeviceResponse(0x01)
  readBytesBulk(amount)
  assertDeviceResponse(0x03)
  assertDeviceResponse(0x00)

def prepareCalibration():
  statusReadTransfer(hb("dd0000001200"))
  statusReadTransfer(hb("dd0000001200"))
  statusReadTransfer(hb("dd0000001200"))
  statusReadTransfer(hb("dd0000001200"))
  basicTransfer(hb("000000000000"))
  extraParameterTransfer(hb("0a0000000800"), hb("1300040002006400"))
  extraParameterTransfer(hb("0a0000000800"), hb("1300040004006400"))
  extraParameterTransfer(hb("0a0000000800"), hb("1300040008006400"))
  extraParameterTransfer(hb("0a0000000800"), hb("1400040002006400"))
  extraParameterTransfer(hb("0a0000000800"), hb("1400040004006400"))
  extraParameterTransfer(hb("0a0000000800"), hb("1400040008006400"))
  extraParameterTransfer(hb("0a0000000600"), hb("950000000000"))
  statusReadTransfer(hb("080000008000"))
  extraParameterTransfer(hb("0a0000000e00"), hb("12000a00800000000000b829e71a"))
  #extraParameterTransfer(hb("0a0000000e00"), hb("12000a0080006f02f0002829f819"))
  extraParameterTransfer(hb("0a0000000600"), hb("170002000100"))
  statusReadTransfer(hb("030000000e00"))
  basicTransfer(hb("000000000000"))
  statusReadTransfer(hb("d70000006700"))
  extraParameterTransfer(hb("dc0000001d00"), hb("00000000000000000000000000000007001a790b00fe0f000000000000"))
  basicTransfer(hb("000000000000"))
 # extraParameterTransfer(hb("150000001000"), hb("000f2c01800404000100000000801000"))
  #extraParameterTransfer(hb("150000001000"), hb("000fb004800404000100000000801000"))
  #extraParameterTransfer(hb("150000001000"), hb("000fb004902004000100000001801000"))
  extraParameterTransfer(hb("150000001000"), hb("000fb004802004000108000001801000"))
  basicTransfer(hb("1b0000000100"))
  basicTransfer(hb("000000000000"))
  statusReadTransfer(hb("d70000006700"))
  extraParameterTransfer(hb("dc0000001d00"), hb("7b1e2f168c10171410000000212121070000790b14000f000000000000"))
  #extraParameterTransfer(hb("dc0000001d00"), hb("7e26661c1515171411000000212121070000790b14000f000000000000"))

def doCalibration():
  prepareCalibration()
  transferLines(0x04, [0xa6e8])
  basicTransfer(hb("000000000000"))
  basicTransfer(hb("000000000000"))
  transferLines(0xac, [0xfff0] * 28 + [0x0ab8])
  statusReadTransfer(hb("d70000006700"))
  extraParameterTransfer(hb("dc0000001d00"), hb("7b1e2f168c10171410000000212121070000790b14000f000000000000"))
  #extraParameterTransfer(hb("dc0000001d00"), hb("7e26661c1515171411000000212121070000790b14000f000000000000"))
  transferLines(0x04, [0xa6e8])
  basicTransfer(hb("000000000000"))
  basicTransfer(hb("000000000000"))
  statusReadTransfer(hb("18000014dc00"))
  statusReadTransfer(hb("0f0000001200"))
  basicTransfer(hb("000000000000"))
  #transferLines(0xd8, [0xfff0, 0x7860])
  #transferLines(0xd8, [0xfff0, 0x7860])
  #transferLines(0xd8, [0xfff0, 0x7860])
  #transferLines(0xd5, [0xfff0, 0x7326])
  #statusReadTransfer(hb("dd0000001200"))
  #statusReadTransfer(hb("dd0000001200"))
  #statusReadTransfer(hb("dd0000001200"))

def prepareScan():
  statusReadTransfer(hb("dd0000001200"))
  statusReadTransfer(hb("dd0000001200"))
  statusReadTransfer(hb("dd0000001200"))
  statusReadTransfer(hb("dd0000001200"))
  basicTransfer(hb("000000000000"))
  extraParameterTransfer(hb("0a0000000800"), hb("1300040002006400"))
  extraParameterTransfer(hb("0a0000000800"), hb("1300040004006400"))
  extraParameterTransfer(hb("0a0000000800"), hb("1300040008006400"))
  extraParameterTransfer(hb("0a0000000800"), hb("1400040002006400"))
  extraParameterTransfer(hb("0a0000000800"), hb("1400040004006400"))
  extraParameterTransfer(hb("0a0000000800"), hb("1400040008006400"))
  extraParameterTransfer(hb("0a0000000600"), hb("950000000000"))
  statusReadTransfer(hb("080000008000"))
  extraParameterTransfer(hb("0a0000000e00"), hb("12000a0080006f02f0002829f819"))
  extraParameterTransfer(hb("0a0000000600"), hb("170002000100"))
  statusReadTransfer(hb("030000000e00"))
  basicTransfer(hb("000000000000"))
  statusReadTransfer(hb("d70000006700"))
  extraParameterTransfer(hb("dc0000001d00"), hb("7e26661c1515171411000000212121070000790b14000f000000000000"))
  basicTransfer(hb("000000000000"))
  extraParameterTransfer(hb("150000001000"), hb("000fb004802004000108000001801000"))
  basicTransfer(hb("1b0000000100"))
  basicTransfer(hb("000000000000"))
  basicTransfer(hb("000000000000"))
  statusReadTransfer(hb("18000014dc00"))
  statusReadTransfer(hb("0f0000001200"))
  basicTransfer(hb("000000000000"))
  basicTransfer(hb("000000000000"))
  basicTransfer(hb("000000000000"))

def transferLines(lineCount, chunkSizes):
  sendHeader()
  sendParameters(bytearray([0x08, 0, 0, 0, lineCount, 0]))
  dev.ctrl_transfer(0xc0, 12, 0x0084, 0, 1)
  for chunk in chunkSizes:
    readBytesBulk(chunk)
  assertDeviceResponse(0x03)
  assertDeviceResponse(0x00)

def transferImage():
  for i in range(18):
    transferLines(0xff, [0xfff0] * 17 + [0xdf20])
  transferLines(0x02, [0x23e0])
  return imageData

def doScan():
  transferImage()

dev = usb.core.find(idVendor=0x05e3, idProduct=0x0145)
doCalibration()
doScan()
