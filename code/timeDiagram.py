#!/usr/bin/python3

import argparse
from subprocess import check_output
import matplotlib.pyplot as plt

def plotValues(values, maxNumber, label):
  xval, yval = [], []
  while len(values) > 0 and values[0][1] <= maxNumber:
      v = values.pop(0)
      xval.append(v[0])
      yval.append(v[1])
  plt.plot(xval, yval, label = label)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile",
                    help = "pcap file", type = str, required = True)
parser.add_argument("-n", "--numbers",
                    help = "maximum packet number per segment",
                    type = int, nargs = "+", required = True)
parser.add_argument("-al", "--axisLabels",
                    help = "strings to label the x and y axis",
                    type = str, nargs = 2, required = True)
parser.add_argument("-ll", "--legendLabels",
                    help = "strings to label each segment in the legend",
                    type = str, nargs = "+", required = True)
parser.add_argument("-o", "--outputFile",
                    help = "image file", type = str, required = True)
args = parser.parse_args()

cmdline = "tshark -r {} -e _ws.col.Time -Tfields"
cmdline = cmdline.format(args.inputFile)

values = []
for l in check_output(cmdline, shell = True).splitlines():
  values.append((float(l), len(values) + 1))

fig, ax = plt.subplots()
ax.set_xlabel(args.axisLabels[0])
ax.set_ylabel(args.axisLabels[1])
for i, n in enumerate(args.numbers):
  plotValues(values, n, args.legendLabels[i])

plt.legend()
plt.savefig(args.outputFile, bbox_inches = "tight", pad_inches = 0)
