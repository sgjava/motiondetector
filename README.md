![Title](images/title.png)

Motion Detector takes input from video sources such as network cameras, web cams, files, etc. and makes intelligent decisions based on analyzing each frame. Motion Detector uses a plugin based event driven architecture that allows you to extend functionality. It is deployed as an intelligent security system, but can be easily configured to your particular scenario.

The primary focus of Motion detector is efficient video processing, fault tolerance and extensibility. While most security themed video monitoring is based on motion detection, Motion Detector places a high value on Computer vision for intelligent frame analysis such as HOG pedestrian and Haar cascade multi-scale detection.

Using the pre-trained Histogram of Oriented Gradients and Linear SVM method works better when objects are larger (green is motion ROI and blue is a detected pedestrian):

![Title](images/hog.jpg)

Using the pre-trained Haar Cascade method works better when objects are smaller:

![Title](images/cascade.jpg)

It's important to use the right detectors and configuration to achieve the desired results.

### Features

* Has been tested on SBCs such as CHIP, ODROID C1/C2/XU4, Pine A64, etc. to create smart cameras.
* Run multiple copies on a central server for IP based cameras.
* Supports several types of video inputs including USB and IP (wired/wireless)
  cameras, video files, etc.
* Fault tolerant architecture ensures buggy camera firmware or poor network
  connectivity will not derail video processing.
* High performance frame capture plugins including Python socket based MJPEG decoder.
* Threshold based motion detection, ignore mask, multiple object marking and video recording.

### Requirements
* X86, X86_64, ARMv7 or ARMv8 version of Ubuntu 16.04 or Debian 8 (will most likely work on other Linux based operating systems as well)
* Internet connection
* Camera or video file
* [Install OpenCV](https://github.com/sgjava/install-opencv) or some other method to install latest OpenCV

### FreeBSD License
Copyright (c) Steven P. Goldsmith

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
