Here I am developing my bachelor thesis on the topic of
**"Developing a driver for a film scanner by means of USB sniffing and reverse engineering"**.

##### Abstract:

> An open-source driver for a film scanner (Reflecta CrystalScan 7200) is created using
reverse engineering techniques. The USB communication between the device and
the supplied vendor software is recorded and analyzed. As a first stage, the transferred
image is reconstructed from the recording.  After that, a program that closely models
that communication is created to perform scanning without the vendor software.
Patterns in the transferred data are studied so scan parameters can be customized.
Image processing operations relevant to optimizing scanner images are described.
The final driver allows for basic operation (receiving usable images) of the device.

As of October 8, 2018 the thesis is now complete.

In addition to the actual thesis, this repository contains tools to scan an image, progressively drawing lines on the screen as the image is received (*scanInteractive.py*), extract the transmitted image based on a Wireshark .pcap file (*extractImage.py*), draw a time diagram of the recorded packets (*timeDiagram.py*), automatically crop a scan to remove areas outside the photo (*crop.py*), and overpaint dust specks in the RGB image using information in the infrared channel (*inpaint.py*). 
