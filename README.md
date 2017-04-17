![Title](images/title.png)

Motion detector takes input from video sources such as network cameras, web cams, files, etc. and makes intelligent decisions based on analyzing each frame. Motion detector uses a plugin based event driven architecture that allows you to extend functionality for a particular use case. It is deployed as an intelligent security system, but can be easily configured to your particular scenario.

The primary focus of Motion detector is efficient video processing, fault tolerance and extensibility. While most security themed video monitoring is based on motion detection, CVP places a high value on Computer vision for intelligent frame analysis such as HOG pedestrian and Haar cascade multi-scale detection.

### Features

* Has been tested on SBCs such as CHIP, ODROID C1/C2/XU4, Pine A64, etc. to create smart cameras.
* Run multiple copies on a central server for IP based cameras.
* Supports several types of video inputs including USB and IP (wired/wireless)
  cameras, video files, etc.
* Fault tolerant architecture ensures buggy camera firmware or poor network
  connectivity will not derail video processing.
* High performance frame capture plugins including Python socket based MJPEG decoder.
* Threshold based motion detection, ignore mask, multiple object marking and recording.

### Requirements
* X86, X86_64, ARMv7 or ARMv8 version of Ubuntu 16.04 or Debian 8 (will most likely work on other Linux based operating systems as well)
* Internet connection
* Camera
* [Install OpenCV](https://github.com/sgjava/install-opencv) or some other method to install latest OpenCV
