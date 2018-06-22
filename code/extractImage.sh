#!/bin/sh
set -e

PCAPFILE=../captures/scan_full.pcapng

./extractImage.py -i $PCAPFILE -bo 300 -bn 2 -ll 1645 -lo 842 -ln 4 -lm 1060 -o out_r.png
./extractImage.py -i $PCAPFILE -bo 300 -bn 2 -ll 1645 -lo 852 -ln 4 -lm 1060 -o out_g.png
./extractImage.py -i $PCAPFILE -bo 300 -bn 2 -ll 1645 -lo 853 -ln 4 -lm 1060 -o out_i.png
./extractImage.py -i $PCAPFILE -bo 300 -bn 2 -ll 1645 -lo 863 -ln 4 -lm 1060 -o out_b.png
convert out_r.png out_g.png out_b.png -combine -gamma 2 out.png
