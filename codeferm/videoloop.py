"""
Created on Apr 13, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import logging, sys, os, traceback, time, datetime, importlib, threading, cv2, numpy, config, motiondet, observer, observable


class videoloop(observer.observer, observable.observable):
    """This class used to acquire and process frames.
    
    The idea here is to keep things moving as fast as possible. Anything that
    would slow down frame processing should be off loaded to a thread or
    background process.
    
    """

    def __init__(self, fileName):
        # Get app configuration
        self.appConfig = config.config(fileName)
        # Set up logger
        self.logger = logging.getLogger("videoloop")
        self.logger.setLevel(self.appConfig.logging['level'])
        formatter = logging.Formatter(self.appConfig.logging['formatter'])
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info("Configuring from file: %s" % fileName)
        self.logger.info("Logging level: %s" % self.appConfig.logging['level'])
        self.logger.debug("Logging formatter: %s" % self.appConfig.logging['formatter'])
        # Get frame grabber plugin
        self.logger.info("Loading frame grabber plugin: %s" % self.appConfig.camera['framePlugin'])
        # If url is a file read fps is timed by the video fps
        self.urlIsFile = os.path.isfile(self.appConfig.camera['url'])
        # If codeferm.videocapture is selected then set VideoCapture properties
        if self.appConfig.camera['framePlugin'] == "codeferm.videocapture":
            self.framePluginInstance = self.getPlugin(moduleName=self.appConfig.camera['framePlugin'], url=self.appConfig.camera['url'])
            self.framePluginInstance.setProperties(self.appConfig.camera['videoCaptureProperties'])
        else:
            self.framePluginInstance = self.getPlugin(moduleName=self.appConfig.camera['framePlugin'], url=self.appConfig.camera['url'], timeout=self.appConfig.camera['socketTimeout'])
        # Frame buffer
        self.frameBuf = []
        # History buffer to capture just before motion
        self.historyBuf = []
        # Buffer used to write frames
        self.writeBuf = []
        self.fps = 0
        self.frameOk = True
        self.writingFrames = False
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

    def readFrames(self):
        """Read frames and append to buffer"""
        # Make sure thread doesn't hang in case of socket time out, etc.
        try:
            # If reading from a video file use its fps
            if self.urlIsFile:
                self.fps
                fpsTime = 1 / float(self.fps)
            while(self.frameOk):
                if self.urlIsFile:
                    start = time.time()
                now = datetime.datetime.now()
                frame = self.framePluginInstance.getFrame()
                if frame is not None:
                    self.frameOk = len(frame) > 0
                else:
                    self.frameOk = False
                if self.frameOk:
                    # Make sure we do not run out of memory
                    if len(self.frameBuf) > self.appConfig.camera['frameBufMax']:
                        self.logger.error("Frame buffer exceeded: %d" % self.appConfig.camera['frameBufMax'])
                        self.frameOk = False
                    else:
                        # Add new image to end of list
                        self.frameBuf.append((self.framePluginInstance.decodeFrame(frame), now))
                if self.urlIsFile:
                    curTime = time.time()
                    elapsed = curTime - start
                    # Try to keep FPS for files consistent otherwise frameBufMax will be reached
                    if elapsed < fpsTime:
                        time.sleep(fpsTime - elapsed)
        except:
            self.frameOk = False
            # Add timestamp to errors
            sys.stderr.write("%s " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f"))
            traceback.print_exc(file=sys.stderr)
        self.logger.info("readFrames thread exit")
        
    def writeFrames(self):
        """Write frames"""
        while(self.writingFrames and self.frameOk):
            # Make sure thread doesn't hang in case of write exception
            try:
                if len(self.writeBuf) > 0:
                    # Write first image in write buffer (the oldest)
                    self.writerPluginInstance.write(self.writeBuf[0][0])
                    self.writeBuf.pop(0)
                    self.recFrameNum += 1
                else:
                    # 1/4 of FPS sleep
                    time.sleep(1.0 / (self.fps * 4))
            except:
                self.writingFrames = False
                # Add timestamp to errors
                sys.stderr.write("%s " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f"))
                traceback.print_exc(file=sys.stderr)
        # Write off write buffer
        self.logger.info("Writing %d frames of write buffer" % len(self.writeBuf))
        for f in self.writeBuf[1:]:
            self.writerPluginInstance.write(f[0])
            self.recFrameNum += 1
        # Empty write buffer
        self.writeBuf = []
        # Write off history buffer
        self.logger.info("Writing %d frames of history buffer" % len(self.historyBuf))
        for f in self.historyBuf[1:]:
            self.writerPluginInstance.write(f[0])
            self.recFrameNum += 1
        self.writerPluginInstance.close()
        # Write off history image
        if self.appConfig.motion['historyImage']:
            # Save history image ready for ignore mask editing
            self.logger.info("Writing history image %s.png" % self.videoFileName)
            cv2.imwrite("%s.png" % self.videoFileName, cv2.bitwise_not(self.historyImg))
        self.notifyObservers(event=self.appConfig.recordingStop, videoFileName=self.videoFileName, frames=self.recFrameNum - 1)
        self.logger.info("writeFrames thread exit")

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
        fileDir = "%s/%s/%s" % (os.path.expanduser(self.appConfig.camera['recordDir']), self.appConfig.camera['name'], dateStr)
        # Create dir if it doesn"t exist
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)
        fileName = "%s-%s.%s" % (name, timestamp.strftime("%H-%M-%S"), self.appConfig.camera['recordFileExt'])
        return "%s/%s" % (fileDir, fileName)

    def recordingStart(self, timestamp, motionPercent):
        "Start recording video"
        # Wait for current recording to finish
        while(self.recording):
            # 1/4 of FPS sleep
            time.sleep(1.0 / (self.fps * 4))        
        self.videoFileName = self.makeFileName(timestamp, "motion")
        self.logger.info("Loading video writer plugin: %s" % self.appConfig.camera['writerPlugin'])
        self.writerPluginInstance = self.getPlugin(moduleName=self.appConfig.camera['writerPlugin'], fileName=self.videoFileName, vcodec=self.appConfig.camera['vcodec'], fps=self.fps, frameWidth=self.framePluginInstance.frameWidth, frameHeight=self.framePluginInstance.frameHeight)
        if self.appConfig.motion['historyImage']:
            # Create black history image
            self.historyImg = numpy.zeros((self.motion.frameResizeHeight, self.motion.frameResizeWidth), numpy.uint8)
        self.recFrameNum = 1
        self.notifyObservers(event=self.appConfig.recordingStart, motionPercent=motionPercent, videoFileName=self.videoFileName, fps=self.fps)
        thread = threading.Thread(target=self.writeFrames)
        thread.start()
       
    def observeEvent(self, **kwargs):
        "Handle events"
        if kwargs["event"] == self.appConfig.motionStart:
            self.logger.debug("Motion start: %4.2f%%" % kwargs["motionPercent"])
            # Kick off recordingStart thread
            recordingStartThread = threading.Thread(target=self.recordingStart, args=(kwargs["timestamp"], kwargs["motionPercent"],))
            recordingStartThread.start()
        elif kwargs["event"] == self.appConfig.motionStop:
            self.logger.debug("Motion stop: %4.2f%%" % kwargs["motionPercent"])
            # Exit writeFrames loop
            self.writingFrames = False
        elif kwargs["event"] == self.appConfig.recordingStart:
            self.logger.info("Recording start: (%4.2f%%) %s @ %3.1f FPS" % (kwargs["motionPercent"], kwargs["videoFileName"], kwargs["fps"]))
            self.recording = True
            self.writingFrames = True
        elif kwargs["event"] == self.appConfig.recordingStop:
            self.logger.info("Recording stop: %d frames, %s" % (kwargs["frames"], kwargs["videoFileName"]))
            self.recording = False
        elif kwargs["event"] == self.appConfig.pedestrianDetected:
            self.logger.debug("Pedestrian detected")
        elif kwargs["event"] == self.appConfig.cascadeDetected:
            self.logger.debug("Cascade detected")
        elif kwargs["event"] == self.appConfig.circleDetected:
            self.logger.debug("Circle detected")

    def waitOnFrameBuf(self):
        """Wait until frame buffer is full"""
        while(self.frameOk and len(self.frameBuf) < self.fps):
            # 1/4 of FPS sleep
            time.sleep(1.0 / (self.fps * 4))

    def run(self):
        """Video processing loop"""
        try:
            # Set FPS
            if self.appConfig.camera['fps'] == 0:
                self.fps = self.framePluginInstance.fps
            else:
                self.fps = self.appConfig.camera['fps']
            self.logger.info("%dx%d, fps: %d" % (self.framePluginInstance.frameWidth, self.framePluginInstance.frameHeight, self.fps))
            if self.framePluginInstance.frameWidth > 0 and self.framePluginInstance.frameHeight > 0:
                # Observe videoloop events
                self.addObserver(self)
                # Analyze only ~3 FPS which works well with this type of detection
                frameToCheck = int(self.fps / 4)
                # 0 means check every frame
                if frameToCheck < 1:
                    frameToCheck = 0
                skipCount = 0
                elapsedFrames = 0    
                # Kick off readFrames thread
                readFramesThread = threading.Thread(target=self.readFrames)
                readFramesThread.start()
                # Wait until frame buffer is full
                self.waitOnFrameBuf()
                # Motion detection object
                self.motion = motiondet.motiondet(self.appConfig, self.frameBuf[0][0], self.logger)
                # Observe motion events
                self.motion.addObserver(self)
                # Load detect plugin
                if self.appConfig.camera['detectPlugin'] != "":
                    self.logger.info("Loading detection plugin: %s" % self.appConfig.camera['detectPlugin'])
                    self.detectPluginInstance = self.getPlugin(moduleName=self.appConfig.camera['detectPlugin'], appConfig=self.appConfig, image=self.frameBuf[0][0], logger=self.logger)
                    # Observe motion events
                    self.detectPluginInstance.addObserver(self)
                if self.appConfig.camera['videoloopPlugins'] is not None:
                    # Load videoloop plugins
                    self.videoloopPluginList = []
                    for item in self.appConfig.camera['videoloopPlugins']:
                        self.logger.info("Loading videoloop plugin: %s" % item)
                        pluginInstance = self.getPlugin(moduleName=item, appConfig=self.appConfig, logger=self.logger)
                        # Observe videoloop events
                        self.addObserver(pluginInstance)
                        self.videoloopPluginList.append(pluginInstance)
                start = time.time()
                # Loop as long as there are frames in the buffer
                while(len(self.frameBuf) > 0):
                    # Calc FPS    
                    elapsedFrames += 1
                    curTime = time.time()
                    elapse = curTime - start
                    # Log FPS
                    if elapse >= self.appConfig.camera['fpsInterval']:
                        start = curTime
                        self.logger.info("%3.1f FPS, frame buffer size: %d, history buffer size: %d" % (elapsedFrames / elapse, len(self.frameBuf), len(self.historyBuf)))
                        elapsedFrames = 0
                        self.notifyObservers(event=self.appConfig.healthCheck, frameBuf=self.frameBuf, fps=self.fps, frameOk=self.frameOk)
                    # Wait until frame buffer is full
                    self.waitOnFrameBuf()
                    # Get oldest frame
                    frame = self.frameBuf[0][0]
                    timestamp = self.frameBuf[0][1]
                    # Buffer oldest frame
                    self.historyBuf.append(self.frameBuf[0])
                    # Toss oldest history frame
                    if len(self.historyBuf) > self.fps:
                        self.historyBuf.pop(0)
                    # Toss oldest frame
                    self.frameBuf.pop(0)
                    # Skip frames until skip count <= 0
                    if skipCount <= 0:
                        skipCount = frameToCheck
                        resizeImg, grayImg, bwImg, motionPercent, movementLocationsFiltered = self.motion.detect(frame, timestamp)
                        if self.appConfig.motion['historyImage'] and self.recording:
                            # Update history image
                            self.historyImg = numpy.bitwise_or(bwImg, self.historyImg)                    
                        if self.appConfig.camera['detectPlugin'] != "":
                            locationsList, foundLocationsList, foundWeightsList = self.detectPluginInstance.detect(frame, resizeImg, grayImg, timestamp, movementLocationsFiltered)
                            if len(foundLocationsList) > 0 and self.recording:
                                # Save off detected elapsedFrames
                                if self.appConfig.camera['saveFrames']:
                                    thread = threading.Thread(target=self.saveFrame, args=(frame, "%s/%d.jpg" % (os.path.splitext(self.videoFileName)[0], self.recFrameNum)),)
                                    thread.start()
                    else:
                        skipCount -= 1
                    # Add frame if recording
                    if self.writingFrames and len(self.historyBuf) > 0:
                            # Write first image in history buffer (the oldest)
                            self.writeBuf.append(self.historyBuf[0])
            # If exiting while writing frames then exit writeFrames loop                
            self.writingFrames = False
            # Wait for current recording to finish
            while(self.recording):
                # 1/4 of FPS sleep
                time.sleep(1.0 / (self.fps * 4))        
            # Close capture
            self.framePluginInstance.close()
        except:
            # Add timestamp to errors
            sys.stderr.write("%s " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f"))
            traceback.print_exc(file=sys.stderr)

                
if __name__ == "__main__":
    try:
        # sys.argv[1] is configuration file or default is used
        if len(sys.argv) < 2:
            fileName = "../config/test.ini"
        else:
            fileName = os.path.expanduser(sys.argv[1])
        videoLoop = videoloop(fileName)
        videoLoop.run()
        # Make sure read/write threads exit
        videoLoop.frameOk = False
        videoLoop.recording = False
        videoLoop.logger.info("Process exit")
    except:
        # Add timestamp to errors
        sys.stderr.write("%s " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f"))
        traceback.print_exc(file=sys.stderr)
