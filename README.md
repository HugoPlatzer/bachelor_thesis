Here I'm developing my bachelor thesis on the topic of
**"Developing a driver for a film scanner by means of USB sniffing and reverse engineering"**.

[View PDF(compiled online)](https://latexonline.cc/compile?git=https%3A%2F%2Fgithub.com%2FHugoPlatzer%2Fbachelor_thesis&target=thesis.tex&command=pdflatex&trackId=1509982456569)

## Schedule

* USB standard: Basics, Endpoints, Transfer types **12.11.**
* Sniffing: hardware devices, software (windows vs. linux),
  my setup: Windows + scanner software in Virtualbox, USB passthrough, wireshark on linux **12.11.**
* basic analysis of captures **26.11.**
* Python / PyUSB: support basic commands: initialization, do scan at certain resolution, data transfer **26.11.**
* Image processing
  * Equalizing brightness per column **12.11.**
  * Brightness / contrast / color-balance **12.11.**
  * Dust / scratch correction: IR channel processing, Inpainting algorithms **3.12.**
  * Image border detection / auto-crop **9.12.**
* SANE
  * why does the existing backend not work for my device?
  (simple fix vs. completely different device) **23.12.**
  * create SANE backend supporting at least the basic features **23.12.**
  * how to integrate dust correction into SANE? **1.1.**
