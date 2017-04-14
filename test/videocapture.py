"""
Created on Apr 12, 2017

@author: sgoldsmith

Copyright (c) Steven P. Goldsmith

All rights reserved.
"""

import unittest, sys, logging, codeferm.config, codeferm.videocapture


class mjpegclient(unittest.TestCase):


    def setUp(self):
        # sys.argv[6] is configuration file or default is used
        if len(sys.argv) < 7:
            fileName = "../config/test.ini"
        else:
            fileName = sys.argv[6]
        print "fileName: %s" % fileName      
        self.appConfig = codeferm.config.config(fileName)
        # Set up logger
        self.logger = logging.getLogger("mjpegclient")
        self.logger.setLevel(self.appConfig.loggingLevel)
        formatter = logging.Formatter(self.appConfig.loggingFormatter)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info("Configuring from file: %s" % fileName)
        self.logger.info("Logging level: %s" % self.appConfig.loggingLevel)
        self.logger.debug("Logging formatter: %s" % self.appConfig.loggingFormatter)
        self.client = codeferm.videocapture.videocapture(self.appConfig.url)

    def tearDown(self):
        self.logger.debug("tearDown")
        self.client.close()

    def testDecode(self):
        self.logger.debug("testDecode")
        frame = self.client.getFrame()
        image = self.client.decodeFrame(frame)
        # Make sure we have image data
        self.assertFalse(image.size == 0, "Image cannot be size 0")
        frameHeight, frameWidth, channels = image.shape
        self.logger.debug("Height: %d, width: %d, channels: %d" % (frameHeight, frameWidth, channels))
        
if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])
