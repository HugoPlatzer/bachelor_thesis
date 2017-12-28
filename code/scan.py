#!/usr/bin/python3

# Control the Reflecta CrystalScan 7200 film scanner

import argparse
import usb.core

parser = argparse.ArgumentParser()
args = parser.parse_args()

dev = usb.core.find(idVendor=0x05e3, idProduct=0x0145)
#print(dev.ctrl_transfer(0xc0, 12, 0x0084, 0, 1))
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
dev.ctrl_transfer(0x40, 12, 0x0085, 0, bytearray.fromhex("dd"))
dev.ctrl_transfer(0x40, 12, 0x0085, 0, bytearray.fromhex("00"))
dev.ctrl_transfer(0x40, 12, 0x0085, 0, bytearray.fromhex("00"))
dev.ctrl_transfer(0x40, 12, 0x0085, 0, bytearray.fromhex("00"))
dev.ctrl_transfer(0x40, 12, 0x0085, 0, bytearray.fromhex("12"))
dev.ctrl_transfer(0x40, 12, 0x0085, 0, bytearray.fromhex("00"))
print(dev.ctrl_transfer(0xc0, 12, 0x0084, 0, 1))
dev.ctrl_transfer(0x40, 4, 0x0082, 0, bytearray.fromhex("0000000012000000"))
print(dev.read(0x81, 12))
print(dev.ctrl_transfer(0xc0, 12, 0x0084, 0, 1))
print(dev.ctrl_transfer(0xc0, 12, 0x0084, 0, 1))
