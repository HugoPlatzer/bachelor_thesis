#!/bin/sh

./timeDiagram.py -i ../captures/scan_main.pcapng \
-n 171 1229 1510 3065 5000 \
-al "Time (seconds)" "Packet count" \
-ll "Idle (before scan)" \
   "Transferring parameters" \
   "Waiting for readiness" \
   "Scan, transferring image data" \
   "Idle (after scan)" \
-o diagram.svg

# convert SVG to PDF for importing into LaTeX documents
inkscape --file=diagram.svg --export-area-drawing --without-gui --export-pdf=diagram.pdf
rm diagram.svg
