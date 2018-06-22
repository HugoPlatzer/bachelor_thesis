#!/bin/sh
set -e

./inpaint.py -i ../images/jpg/imgproc_inpaint_1.jpg -o "1 iteration" -n 1 -m ../images/jpg/imgproc_inpaint_mask.jpg -v &
./inpaint.py -i ../images/jpg/imgproc_inpaint_1.jpg -o "10 iterations" -n 10 -m ../images/jpg/imgproc_inpaint_mask.jpg -v &
./inpaint.py -i ../images/jpg/imgproc_inpaint_1.jpg -o "100 iterations" -n 100 -m ../images/jpg/imgproc_inpaint_mask.jpg -v &
