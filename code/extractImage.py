#!/usr/bin/python3

# Extracts image data from USB communication captures (pcap format)
# of the Reflecta CrystalScan 7200 film scanner

from subprocess import check_output
from PIL import Image
import argparse
from math import ceil

def offset(data, n):
  return data[n:]

def everyNth(data, n):
  return data[::n]

def chunks(data, n):
  return [data[i:i + n] for i in range(0, len(data), n)]

parser = argparse.ArgumentParser()
parser.add_argument("pcapFile")
parser.add_argument("byteOffset", type = int)
parser.add_argument("nthByte", type = int)
parser.add_argument("bytesPerLine", type = int)
parser.add_argument("lineOffset", type = int)
parser.add_argument("nthLine", type = int)
parser.add_argument("pngFile")
args = parser.parse_args()

# Use tshark for parsing the input file
# get payload from all packets incoming on endpoint 1

# IMPORTANT: configure wireshark / tshark not to decode any protocols except USB
# otherwise some packets' payload will not be printed as it's misinterpreted as some protocol
cmdline = "tshark -Tfields -r {} -Y 'usb.endpoint_number == 0x81' -e usb.capdata | tr -d ':'"
cmdline = cmdline.format(args.pcapFile, args.minPacketSize)

# concatenate bytes from all packets

imageBytes = b""
trigger = False

for l in check_output(cmdline, shell = True).splitlines():
  newBytes = bytearray.fromhex(l.decode("utf-8"))
  print(len(newBytes))
  imageBytes += newBytes

imageBytes = offset(imageBytes, args.byteOffset)
imageBytes = everyNth(imageBytes, args.nthByte)
imageLines = chunks(imageBytes, args.bytesPerLine)
imageLines = offset(imageLines, args.lineOffset)
imageLines = everyNth(imageLines, args.nthLine)

print(len(imageLines))

im = Image.new("L", (len(imageLines[0]), len(imageLines)))
print("image dimensions: {}x{}".format(im.size[0], im.size[1]))
px = im.load()

for lineNr, line in enumerate(imageLines):
  for byteNr, byte in enumerate(line):
    px[byteNr, lineNr] = byte

im.save(args.pngFile, "PNG")
