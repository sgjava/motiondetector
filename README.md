![Title](images/title.png)

Motion Detector takes input from video sources such as network cameras, web cams, files, etc. and makes intelligent decisions based on analyzing frames. Motion Detector uses a plugin based event driven architecture that allows you to extend functionality easily. It is deployed as an intelligent security system, but can be configured for your particular scenario.

The primary focus of Motion Detector is efficient video processing, fault tolerance and extensibility. While most security themed video monitoring is based on motion detection, Motion Detector places a high value on Computer Vision for intelligent frame analysis such as HOG pedestrian and Haar cascade multi-scale detection.

Using the pre-trained Histogram of Oriented Gradients and Linear SVM method works better when objects are larger (green is motion ROI and blue is a detected pedestrian):

![Title](images/hog.jpg)

Using the pre-trained Haar Cascade method works better when objects are smaller:

![Title](images/cascade.jpg)

It's important to use the right detectors and configuration to achieve the desired results.

### Features
* Motion Detector has been tested on SBCs such as CHIP, ODROID C1/C2/XU4, Pine A64, etc. to create smart cameras.
* Run multiple copies on a central server for IP based cameras.
* Supports several types of video inputs including USB and IP (wired/wireless)
  cameras, video files, etc.
* Fault tolerant architecture ensures buggy camera firmware or poor network
  connectivity will not derail video processing.
* High performance frame capture plugins including Python socket based MJPEG decoder.
* Threshold based motion detection, ignore mask, multiple object marking and video recording.
* Pedestrian and human feature detection
* Add your own plugins!

### Requirements
* X86, X86_64, ARMv7 or ARMv8 version of Ubuntu 16.04 or Debian 8 (will most likely work on other Linux based operating systems as well)
* Internet connection
* Camera or video file
* [Install OpenCV](https://github.com/sgjava/install-opencv) or some other method to install latest OpenCV

### Download project and test
* `sudo apt-get install git-core`
* `cd ~/`
* `git clone --depth 1 https://github.com/sgjava/motiondetector.git`
* `cd ~/motiondetector/codeferm`
* `export PYTHONPATH=$PYTHONPATH:~/motiondetector`
* `python videoloop.py`
  You should see the video process and create output in ~/motion
  
### Motion Detection
From experience I can tell you that you need to understand the usage scenario. Simple motion detection will work well with static backgrounds, but using it outside you have to deal with cars, tree branches blowing, sudden light changes, etc. This is why built in motion detection is mostly useless on security cameras for these types of scenarios. You can use ignore bitmaps and ROI (regions of interest) to improve results with dynamic backgrounds. For instance, I can ignore my palm tree, but trigger motion if you walk in my doorway.

#### Boosting Performance
I see a lot of posts on the Internet about OpenCV performance on various ARM based SBCs being CPU intensive or slow frame capture, etc. Over time I learned the tricks of the trade and kicked it up a few notches from my own research. These techniques may not work for all usage scenarios or OpenCV functions, but they do work well for security type applications.

Problem: Slow or inconsistent FPS using USB camera.

Solution: Use MJPEG compatible USB camera, mjpg-streamer and my [mjpegclient.py](https://github.com/sgjava/motiondetector/blob/master/codeferm/mjpegclient.py).

Solution: Use threading and a frame buffer to get consistent FPS from camera. Even with recording video and background events you will get very consistent FPS from cameras that allow you to set the FPS. Some cameras have dynamic FPS based on contrast and light. This can be tricky when dealing with fixed FPS video codecs.

Problem: OpenCV functions max out the CPU resulting in low FPS.

Solution: Resize image before any processing. Check out [Pedestrian Detection OpenCV](http://www.pyimagesearch.com/2015/11/09/pedestrian-detection-opencv) as it covers reduction in detection time and improved detection accuracy. The pedestrian HOG detector was trained with 64 x 128 images, so a 320x240 image is fine for some scenarios. As you go up in resolution you get even better performance versus operating on the full sized image. This article also touches on non-maxima suppression which is basically removing overlapping rectangles from detection type functions.

Solution: Sample only some frames. Motion detection using the moving average algorithm works best at around 3 or 4 FPS. This works to your advantage since that is an ideal time to do other types of detection such as for pedestrians. This also works out well as your camera FPS goes higher. That means ~3 FPS are processed even at 30 FPS. You still have to consider video recording overhead since that's still 30 FPS.

Solution: Analyze only motion ROI (regions of interest). By analyzing only ROI you can cut down processing time tremendously. For instance, if only 10% of the frame has motion then the OpenCV function should run about 900% faster! This may not work where there's a large change frame after frame. Luckily this will not happen for most security type scenarios. If a region is too small for the detector it is not processed thus speeding things up even more.

#### Run Motion Detection
If you wish to use the SCP plugin then you should generate ssh keypair, so you do not have to pass passwords around or save them in a file. It's handy to scp video files to a central server or cloud storage after detection.
* ssh-keygen
* ssh-copy-id user@host

The default [test.ini](https://github.com/sgjava/motiondetector/blob/master/config/test.ini) is configured to detect pedestrians from a local video file in the project. Try this first and make sure it works properly.
* `cd ~/motiondetector/codeferm`
* `export PYTHONPATH=$PYTHONPATH:~/motiondetector`
* `python videoloop.py`
* Video will record to ~/motion/test using camera name (default test), date for directory and time for file name
* This is handy for debugging issues or fine tuning using the same file over and over

### Configure supervisor
To make Motion Detector more resilient it's wise to run it with a process control system like [Supervisor](http://supervisord.org). Motion Detector currently fails fast if it gets a bad frame or socket timeout (as long as you use a reasonable socket timeout value in the configuration). Supervisor will automatically restart videoloop.py after failure.
* `sudo apt-get install supervisor`
* `sudo service supervisor start`
* `sudo nano /etc/supervisor/conf.d/videoloop.conf`
```
[program:videoloop]
command = python videoloop.py /path/to/your/config.ini
directory = /home/<username>/motiondetector/codeferm
user = <username>
autostart = true  
autorestart = true  
stdout_logfile = /var/log/supervisor/videoloop.log  
stderr_logfile = /var/log/supervisor/videoloop.log
environment = PYTHONPATH=/home/<username>/motiondetector
```
   
* `sudo supervisorctl update`
* `tail /var/log/supervisor/videoloop.log`

### FreeBSD License
Copyright (c) Steven P. Goldsmith

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
