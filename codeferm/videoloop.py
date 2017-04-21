"""
Created on Apr 13, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import logging, sys, os, traceback, time, datetime, importlib, threading, cv2, numpy, config, motiondet, observer, observable

class videoloop(observer.observer, observable.observable):
    """Main class used to acquire and process frames.
    
    The idea here is to keep things moving as fast as possible. Anything that
    would slow down frame processing should be off loaded to a thread or
    background process.
    
    """

    def __init__(self, fileName):
        # Get app configuration
        self.appConfig = config.config(fileName)        
        # Set up logger
        self.logger = logging.getLogger("videoloop")
        self.logger.setLevel(self.appConfig.loggingLevel)
        formatter = logging.Formatter(self.appConfig.loggingFormatter)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info("Configuring from file: %s" % fileName)
        self.logger.info("Logging level: %s" % self.appConfig.loggingLevel)
        self.logger.debug("Logging formatter: %s" % self.appConfig.loggingFormatter)
        # Get frame grabber plugin
        self.logger.info("Loading frame grabber plugin: %s" % self.appConfig.framePlugin)
        # If url is a file read fps is timed by the video fps
        self.urlIsFile = os.path.isfile(self.appConfig.url)
        # If codeferm.videocapture is selected then set VideoCapture properties
        if self.appConfig.framePlugin == "codeferm.videocapture":
            self.framePluginInstance = self.getPlugin(moduleName=self.appConfig.framePlugin, url=self.appConfig.url)
            self.framePluginInstance.setProperties(self.appConfig.videoCaptureProperties)
        else:
            self.framePluginInstance = self.getPlugin(moduleName=self.appConfig.framePlugin, url=self.appConfig.url, timeout = self.appConfig.socketTimeout)
        self.logger.info("%dx%d, fps: %d" % (self.framePluginInstance.frameWidth, self.framePluginInstance.frameHeight, self.framePluginInstance.fps))
        self.videoWriter = None
        # History buffer to capture just before motion
        self.historyBuf = []
        self.fps = 0
        self.frameOk = True
        self.recording = False
        self.recFrameNum = 0

    def getPlugin(self, moduleName, **kwargs):
        """Dynamically load module"""
        # If package name passed then parse out class name
        moduleSplit = moduleName.split(".")
        if len(moduleSplit) > 1:
            moduleClass = moduleSplit[1]
        else:
            moduleClass = moduleName
        module = importlib.import_module(moduleName)
        moduleClass = getattr(module, moduleClass)
        return moduleClass(**kwargs)

    def readFrames(self, frameBuf):
        """Read frames and append to buffer"""
        # If reading from a video file use its fps
        if self.urlIsFile:
            self.fps
            fpsTime = 1 / float(self.fps)
        while(self.frameOk):
            if self.urlIsFile:
                start = time.time()
            now = datetime.datetime.now()
            # Make sure thread doesn't hang in case of socket time out, etc.
            try:
                frame = self.framePluginInstance.getFrame()
                self.frameOk = len(frame) > 0
                if self.frameOk:
                    # Make sure we do not run out of memory
                    if len(frameBuf) > self.appConfig.frameBufMax:
                        self.logger.error("Frame buffer exceeded: %d" % self.appConfig.frameBufMax)
                        self.frameOk = False
                    else:
                        # Add new image to end of list
                        frameBuf.append((self.framePluginInstance.decodeFrame(frame), now))
                if self.urlIsFile:
                    curTime = time.time()
                    elapsed = curTime - start
                    # Try to keep FPS for files consistent otherwise frameBufMax will be reached
                    if elapsed < fpsTime:
                        time.sleep(fpsTime - elapsed)
            except:
                self.frameOk = False
        self.logger.info("Exiting readFrames thread")

    def saveFrame(self, frame, fileName):
        """Save frame"""
        fileDir = os.path.dirname(fileName)
        # Create dir if it doesn"t exist
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)
        cv2.imwrite(fileName, frame)        

    def makeFileName(self, timestamp, name):
        "Create file name based on image timestamp"
        # Construct directory name from camera name, recordDir and date
        dateStr = timestamp.strftime("%Y-%m-%d")
        fileDir = "%s/%s/%s" % (os.path.expanduser(self.appConfig.recordDir), self.appConfig.cameraName, dateStr)
        # Create dir if it doesn"t exist
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)
        fileName = "%s-%s.%s" % (name, timestamp.strftime("%H-%M-%S"), self.appConfig.recordFileExt)
        return "%s/%s" % (fileDir, fileName)

    def startRecording(self, timestamp, motionPercent):
        "Start recording video"
        self.videoFileName = self.makeFileName(timestamp, "motion")
        self.videoWriter = cv2.VideoWriter(self.videoFileName, cv2.VideoWriter_fourcc(self.appConfig.fourcc[0], self.appConfig.fourcc[1], self.appConfig.fourcc[2], self.appConfig.fourcc[3]), self.fps, (self.framePluginInstance.frameWidth, self.framePluginInstance.frameHeight), True)
        self.logger.info("Start recording (%4.2f) %s @ %3.1f FPS" % (motionPercent, self.videoFileName, self.fps))
        if self.appConfig.historyImage:
            # Create black history image
            self.historyImg = numpy.zeros((self.motion.frameResizeHeight, self.motion.frameResizeWidth), numpy.uint8)
        self.recFrameNum = 1
        self.recording = True
        self.notifyObservers(event=self.appConfig.startRecording, videoFileName=self.videoFileName)

    def stopRecording(self, motionPercent):
        "Stop recording video"
        self.recording = False
        # Write off frame buffer skipping frame already written
        self.logger.info("Writing %d frames of history buffer" % len(self.historyBuf))
        for f in self.historyBuf[1:]:
            self.videoWriter.write(f[0])
            self.recFrameNum += 1
        del self.videoWriter
        self.logger.info("Stop recording, %d frames" % (self.recFrameNum-1))
        # Write off history image
        if self.appConfig.historyImage:
            # Save history image ready for ignore mask editing
            self.logger.info("Writing history image %s.png" % self.videoFileName)
            cv2.imwrite("%s.png" % self.videoFileName, cv2.bitwise_not(self.historyImg))
        self.notifyObservers(event=self.appConfig.stopRecording, videoFileName=self.videoFileName)
        
    def observeEvent(self, **kwargs):
        "Handle events"
        if kwargs["event"] == self.appConfig.motionStart:
            self.logger.debug("Motion start: %4.2f%%" % kwargs["motionPercent"])
            # Kick off startRecording thread
            startRecordingThread = threading.Thread(target=self.startRecording, args=(kwargs["timestamp"], kwargs["motionPercent"],))
            startRecordingThread.start()
        elif kwargs["event"] == self.appConfig.motionStop:
            self.logger.debug("Motion stop: %4.2f%%" % kwargs["motionPercent"])
            # Kick off stopRecording thread
            stopRecordingThread = threading.Thread(target=self.stopRecording, args=(kwargs["motionPercent"],))
            stopRecordingThread.start()
        elif kwargs["event"] == self.appConfig.pedestrianDetected:
            self.logger.debug("Pedestrian detected")
        elif kwargs["event"] == self.appConfig.cascadeDetected:
            self.logger.debug("Cascade detected")

    def waitOnFrameBuf(self, frameBuf):
        """Wait until frame buffer is full"""
        while(self.frameOk and len(frameBuf) < self.fps):
            # 1/4 of FPS sleep
            time.sleep(1.0 / (self.fps * 4))

    def run(self):
        """Video processing loop"""
        frameWidth = self.framePluginInstance.frameWidth
        frameHeight = self.framePluginInstance.frameHeight
        # See if plug in has FPS set
        if self.framePluginInstance.fps == 0:
            self.fps = self.appConfig.fps
        elif self.appConfig.fps == 0:
            self.fps = self.framePluginInstance.fps
        else:
            self.fps = self.appConfig.fps
        if frameWidth > 0 and frameHeight > 0:
            # Analyze only ~3 FPS which works well with this type of detection
            frameToCheck = int(self.fps / 4)
            # 0 means check every frame
            if frameToCheck < 1:
                frameToCheck = 0
            skipCount = 0
            elapsedFrames = 0    
            # Frame buffer
            frameBuf = []
            # Kick off readFrames thread
            readFramesThread = threading.Thread(target=self.readFrames, args=(frameBuf,))
            readFramesThread.start()
            # Wait until frame buffer is full
            self.waitOnFrameBuf(frameBuf)
            # Motion detection object
            self.motion = motiondet.motiondet(self.appConfig, frameBuf[0][0], self.logger)
            # Observe motion events
            self.motion.addObserver(self)
            # Load detect plugin
            if self.appConfig.detectPlugin != "":
                self.logger.info("Loading detection plugin: %s" % self.appConfig.detectPlugin)
                self.detectPluginInstance = self.getPlugin(moduleName=self.appConfig.detectPlugin, appConfig = self.appConfig, image = frameBuf[0][0], logger = self.logger)
                # Observe motion events
                self.detectPluginInstance.addObserver(self)
            if self.appConfig.videoloopPlugins is not None:
                # Load videoloop plugins
                self.videoloopPluginList = []
                for item in self.appConfig.videoloopPlugins:
                    self.logger.info("Loading videoloop plugin: %s" % item)
                    pluginInstance = self.getPlugin(moduleName=item, appConfig = self.appConfig, logger = self.logger)
                    # Observe videoloop events
                    self.addObserver(pluginInstance)
                    self.videoloopPluginList.append(pluginInstance)
            start = time.time()
            # Loop as long as there are frames in the buffer
            while(len(frameBuf) > 0):
                # Calc FPS    
                elapsedFrames += 1
                curTime = time.time()
                elapse = curTime - start
                # Log FPS
                if elapse >= self.appConfig.fpsInterval:
                    start = curTime
                    self.logger.info("%3.1f FPS, frame buffer size: %d" % (elapsedFrames / elapse, len(frameBuf)))
                    elapsedFrames = 0                
                # Wait until frame buffer is full
                self.waitOnFrameBuf(frameBuf)
                # Get oldest frame
                frame = frameBuf[0][0]
                timestamp = frameBuf[0][1]
                # Buffer oldest frame
                self.historyBuf.append(frameBuf[0])
                # Toss oldest history frame
                if len(self.historyBuf) > self.fps:
                    self.historyBuf.pop(0)
                # Toss oldest frame
                frameBuf.pop(0)
                # Skip frames until skip count <= 0
                if skipCount <= 0:
                    skipCount = frameToCheck
                    resizeImg, grayImg, bwImg, motionPercent, movementLocationsFiltered = self.motion.detect(frame, timestamp)
                    if self.appConfig.historyImage and self.recording:
                        # Update history image
                        self.historyImg = numpy.bitwise_or(bwImg, self.historyImg)                    
                    if self.appConfig.detectPlugin != "":
                        locationsList, foundLocationsList, foundWeightsList = self.detectPluginInstance.detect(frame, resizeImg, timestamp, movementLocationsFiltered)
                        if len(foundLocationsList) > 0 and self.recording:
                            # Save off detected elapsedFrames
                            if self.appConfig.saveFrames:
                                thread = threading.Thread(target=self.saveFrame, args=(frame, "%s/%d.jpg" % (os.path.splitext(self.videoFileName)[0], self.recFrameNum)),)
                                thread.start()
                else:
                    skipCount -= 1
                # Write frame if recording
                if self.recording:
                    if len(self.historyBuf) > 0:
                        # Write first image in history buffer (the oldest)
                        self.videoWriter.write(self.historyBuf[0][0])
                        self.recFrameNum += 1
        # If exiting while recording then stop recording                
        if self.recording:
            self.stopRecording(0.0)
        # Close capture
        self.framePluginInstance.close()
                
if __name__ == "__main__":
    try:
        # sys.argv[1] is configuration file or default is used
        if len(sys.argv) < 2:
            fileName = "../config/test.ini"
        else:
            fileName = sys.argv[1]
        videoLoop = videoloop(fileName)
        videoLoop.run()
        videoLoop.logger.info("Process exit")
    except:
        # Add timestamp to errors
        sys.stderr.write("%s " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f"))
        traceback.print_exc(file=sys.stderr)
