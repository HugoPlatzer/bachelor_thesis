#!/usr/bin/python3

# Extracts image data from USB communication captures (pcap format)
# of the Reflecta CrystalScan 7200 film scanner

import argparse
from subprocess import check_output
from PIL import Image

# Filters for processing the input bytes
def offset(data, n):
  return data[n:]
  
def upto(data, n):
  return data[:n]

def everyNth(data, n):
  return data[::n]

def chunks(data, n):
  return [data[i:i + n] for i in range(0, len(data), n)]

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", help = "pcap file", type = str, required = True)
parser.add_argument("-bo", "--byteOffset", type = int, default = 0)
parser.add_argument("-bn", "--byteNth", type = int, default = 1)
parser.add_argument("-ll", "--lineLength", type = int, required = True)
parser.add_argument("-lo", "--lineOffset", type = int, default = 0)
parser.add_argument("-ln", "--lineNth", type = int, default = 1)
parser.add_argument("-lm", "--lineMax", type = int)
parser.add_argument("-o", "--outputFile", help = "png file", type = str, required = True)
args = parser.parse_args()

# Use tshark for parsing the input file
# get payload from all packets incoming on endpoint 1

# IMPORTANT: configure wireshark / tshark not to decode any protocols except USB
# otherwise some packets' payload will not be printed as it's misinterpreted as some protocol
cmdline = "tshark -r {} -Y 'usb.endpoint_number == 0x81' -e usb.capdata -T fields"
cmdline = cmdline.format(args.inputFile)

# concatenate bytes from all packets, then apply filters
imageBytes = bytearray()

for l in check_output(cmdline, shell = True).splitlines():
  newBytes = bytearray.fromhex(l.decode("utf-8").replace(":", ""))
  imageBytes += newBytes

print("read {} bytes".format(len(imageBytes)))

imageBytes = offset(imageBytes, args.byteOffset)
imageBytes = everyNth(imageBytes, args.byteNth)
imageLines = chunks(imageBytes, args.lineLength)
imageLines = offset(imageLines, args.lineOffset)
imageLines = everyNth(imageLines, args.lineNth)
if args.lineMax is not None:
  imageLines = upto(imageLines, args.lineMax)

# write one grayscale PNG image
im = Image.new("L", (len(imageLines[0]), len(imageLines)))
print("image dimensions: {}x{}".format(im.size[0], im.size[1]))
px = im.load()

for lineNr, line in enumerate(imageLines):
  for byteNr, byte in enumerate(line):
    px[byteNr, lineNr] = byte

im.save(args.outputFile, "PNG")
