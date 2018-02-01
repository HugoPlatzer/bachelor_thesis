Here I'm developing my bachelor thesis on the topic of
**"Developing a driver for a film scanner by means of USB sniffing and reverse engineering"**.

[View PDF(compiled online)](https://latexonline.cc/compile?git=https%3A%2F%2Fgithub.com%2FHugoPlatzer%2Fbachelor_thesis&target=thesis.tex&command=pdflatex&trackId=1509982456569)

## Aspects remaining (as of 01.02.2018)

* Controlling the scanner
  * Describe transaction patterns, also with diagrams
  * Describe complete data traffic during a scan using these patterns
  * Meaning of bytes in sequence, for most important parameters:
    * Resolution, color mode, scan area, exposure level
  * Retrieving image / calibration data
    * Calculating amount of rows, bytes per row
    * Image retrieval transaction
  * Timing: Describe readiness query / sleep, time diagram during scan
* Image processing
  * Applying calibration / shading data
  * Basic processing
    * Invert negative, remove orange mask
    * Color balance
    * gamma, contrast, brightness, saturation
  * Digital ICE / Dust correction
    * Build mask from IR channel
    * Describe good inpainting algorithms
  * Autocrop
* SANE
  * Try to make existing driver work
  * If not possible, implement basic driver
  * Describe SANE architecture
* Polishing
  * Replace diagrams from books by drawing them in Inkscape
  * Compile information on scanner control into appendix
  * Work on layout, tables
* Finer points
  * Wakeup after standby, abort during scan
  * 7200 dpi only in vertical dimension (downscale in image processing)
