"""
Created on Feb 9, 2013

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import logging, sys, traceback, datetime, importlib, config

class videoloop(object):
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
        self.framePluginInstance = self.getPlugin(moduleName=self.appConfig.framePlugin, url=self.appConfig.url)
        # If codeferm.videocapture is selected then set VideoCapture properties
        if self.appConfig.framePlugin == "codeferm.videocapture":
            self.framePluginInstance.setProperties(self.appConfig.videoCaptureProperties)
        self.logger.debug("Height: %d, width: %d, fps: %d" % (self.framePluginInstance.frameHeight, self.framePluginInstance.frameWidth, self.framePluginInstance.fps))
                                 

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

    def run(self):
        """Video processing loop"""
        pass

if __name__ == "__main__":
    try:
        # sys.argv[1] is configuration file or default is used
        if len(sys.argv) < 2:
            fileName = "../config/test.ini"
        else:
            fileName = sys.argv[1]
        videoLoop = videoloop(fileName)
        videoLoop.run()
    except:
        sys.stderr.write("%s " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f"))
        traceback.print_exc(file=sys.stderr)
    # Do cleanup
    if videoLoop:
        videoLoop.framePluginInstance.close()
