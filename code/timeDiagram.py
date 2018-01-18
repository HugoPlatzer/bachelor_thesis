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
parser.add_argument("-i", "--inputFile", help = "pcap file", type = str, required = True)
parser.add_argument("-n", "--numbers", help = "maximum packet number per segment", type = int, nargs = "+", required = True)
parser.add_argument("-l", "--labels", help = "strings to describe each segment", type = str, nargs = "+", required = True)
parser.add_argument("-o", "--outputFile", help = "image file", type = str, required = True)
args = parser.parse_args()

cmdline = "tshark -r {} -e _ws.col.Time -Tfields"
cmdline = cmdline.format(args.inputFile)

values = []
for l in check_output(cmdline, shell = True).splitlines():
  values.append((float(l), len(values) + 1))

fig, ax = plt.subplots()
ax.set_xlabel("Zeit (Sekunden)")
ax.set_ylabel("Paketnummer")

for i, n in enumerate(args.numbers):
  plotValues(values, n, args.labels[i])

plt.tight_layout()
plt.legend()
plt.savefig(args.outputFile)
