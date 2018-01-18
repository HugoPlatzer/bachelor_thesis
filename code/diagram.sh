#!/bin/sh

./timeDiagram.py -i ../captures/scan_main.pcapng \
-n 171 1229 1510 3065 5000 \
-l "Leerlauf (vor Scan)" \
   "Übertragen der Parameter" \
   "Warten auf Bereitschaft" \
   "Scannen, Übertragen der Bilddaten" \
   "Leerlauf (nach Scan)" \
-o diagram.svg
