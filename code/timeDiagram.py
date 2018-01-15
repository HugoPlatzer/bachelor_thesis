#!/usr/bin/python3

import argparse
from subprocess import check_output
import matplotlib.pyplot as plt

def do_plot(values, maxI, label):
  xval, yval = [], []
  while len(values) > 0 and values[0][0] < maxI:
      v = values.pop(0)
      xval.append(v[0])
      yval.append(v[1])
  plt.plot(xval, yval, label = label)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inputFile", help = "pcap file", type = str, required = True)
parser.add_argument("-o", "--outputFile", help = "image file", type = str, required = True)
args = parser.parse_args()

cmdline = "tshark -r {} -e _ws.col.Time -Tfields"
cmdline = cmdline.format(args.inputFile)

timestamps = []

for l in check_output(cmdline, shell = True).splitlines():
  timestamps.append((len(timestamps), float(l)))

fig, ax = plt.subplots()
ax.set_xlabel("Paketnummer")
ax.set_ylabel("Zeit (Sekunden)")
plt.tight_layout()
do_plot(timestamps, 181, "Leerlauf (vor Scan)")
do_plot(timestamps, 1229, "Übertragung der Parameter")
do_plot(timestamps, 1510, "Warten auf Bereitschaft")
do_plot(timestamps, 3065, "Scannen, Übertragen der Bilddaten")
do_plot(timestamps, 100000, "Leerlauf (nach Scan)")
plt.legend()

#plt.show()
plt.savefig(args.outputFile)
